"""Runtime factories for storage and retrieval backends."""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3

from apps.api.runtime_storage import StorageRuntimeConfig
from src.layer1_contracts.interfaces.lexical_store import LexicalStoreInterface
from src.layer1_contracts.interfaces.metadata_store import MetadataStoreInterface
from src.layer1_contracts.interfaces.sql_executor import SQLExecutorInterface
from src.layer1_contracts.interfaces.vector_store import VectorStoreInterface
from src.layer4_providers.stores.metadata.sqlite_adapter import SQLiteMetadataStore
from src.layer4_providers.stores.postgres.connection import PostgresSQLExecutor
from src.layer4_providers.stores.postgres.lexical_adapter import PostgresLexicalStore
from src.layer4_providers.stores.postgres.metadata_adapter import PostgresMetadataStore
from src.layer4_providers.stores.postgres.vector_adapter import PostgresVectorStore
from src.layer4_providers.stores.qdrant.adapter import QdrantAdapter
from src.layer4_providers.stores.sqlite_fts.adapter import SQLiteFTSAdapter


@dataclass(frozen=True)
class RuntimeStores:
    """Resolved storage adapters for the current runtime."""

    metadata_store: MetadataStoreInterface
    vector_store: VectorStoreInterface
    lexical_store: LexicalStoreInterface
    sql_executor: SQLExecutorInterface | None


class SQLiteSQLExecutor(SQLExecutorInterface):
    """SQLite-backed structured-query executor for local development."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def execute(self, sql: str, parameters: list[object] | tuple[object, ...]):
        """Execute one readonly SQL statement."""
        connection = sqlite3.connect(self.db_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        try:
            cursor = connection.execute(sql, parameters)
            rows = cursor.fetchall() if cursor.description else []
            return _SQLiteBufferedCursor(rows=rows, description=cursor.description)
        finally:
            connection.close()

    def ensure_supporting_views(self) -> None:
        """Expose the legacy documents view on the SQLite chunk metadata table."""
        connection = sqlite3.connect(self.db_path, check_same_thread=False)
        try:
            existing_objects = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
                ).fetchall()
            }
            if "documents" in existing_objects or "chunk_metadata" not in existing_objects:
                return
            connection.execute(
                """
                CREATE VIEW IF NOT EXISTS documents AS
                SELECT
                    document_id,
                    MAX(document_title) AS document_title,
                    MAX(document_type) AS document_type,
                    MAX(tags) AS tags,
                    MAX(trust_score) AS trust_score,
                    MAX(created_at) AS created_at,
                    COUNT(*) AS chunk_count
                FROM chunk_metadata
                GROUP BY document_id
                """
            )
            connection.commit()
        finally:
            connection.close()


class _SQLiteBufferedCursor:
    """Buffered cursor wrapper for the SQLite structured-query path."""

    def __init__(self, rows: list[sqlite3.Row], description: object) -> None:
        self._rows = rows
        self.description = description

    def fetchall(self) -> list[sqlite3.Row]:
        """Return all fetched rows."""
        return self._rows


def build_runtime_stores(
    storage: StorageRuntimeConfig,
    embed_dimensions: int,
) -> RuntimeStores:
    """Build runtime storage adapters from deployment config."""
    if storage.database_url:
        return RuntimeStores(
            metadata_store=PostgresMetadataStore(storage.database_url),
            vector_store=PostgresVectorStore(storage.database_url, dimensions=embed_dimensions),
            lexical_store=PostgresLexicalStore(storage.database_url),
            sql_executor=PostgresSQLExecutor(storage.database_url),
        )

    return RuntimeStores(
        metadata_store=SQLiteMetadataStore(db_path=str(storage.metadata_db_path)),
        vector_store=QdrantAdapter(
            url=storage.qdrant_url,
            api_key=storage.qdrant_api_key,
            collection=storage.qdrant_collection,
            dimensions=embed_dimensions,
        ),
        lexical_store=SQLiteFTSAdapter(db_path=str(storage.lexical_db_path)),
        sql_executor=SQLiteSQLExecutor(str(storage.metadata_db_path)),
    )
