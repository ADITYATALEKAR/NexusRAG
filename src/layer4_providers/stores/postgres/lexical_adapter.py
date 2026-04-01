"""Postgres full-text lexical search adapter for Neon."""

from __future__ import annotations

from src.layer1_contracts.interfaces.lexical_store import LexicalStoreInterface
from src.layer4_providers.stores.postgres.connection import connect_postgres


class PostgresLexicalStore(LexicalStoreInterface):
    """Lexical search implemented with Postgres full-text search."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    async def index(self, id: str, content: str, metadata: dict | None = None) -> None:
        """No-op because lexical indexing is maintained on the chunks table itself."""
        return None

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter: dict | None = None,
    ) -> list[tuple[str, float]]:
        """Search chunk content using Postgres full-text search."""
        if not query.strip():
            return []

        sql = """
            SELECT
                id AS chunk_id,
                ts_rank_cd(search_vector, websearch_to_tsquery('english', %s)) AS score
            FROM chunks
            WHERE search_vector @@ websearch_to_tsquery('english', %s)
        """
        params: list[object] = [query, query]
        if filter and "document_id" in filter:
            sql += " AND document_id = %s"
            params.append(filter["document_id"])
        sql += " ORDER BY score DESC LIMIT %s"
        params.append(top_k)

        with connect_postgres(self.database_url) as connection:
            rows = connection.execute(sql, tuple(params)).fetchall()
        return [(row["chunk_id"], float(row["score"])) for row in rows]

    async def delete(self, id: str) -> bool:
        """Delete is handled by metadata deletion; this is a safe no-op."""
        return True

    async def health_check(self) -> bool:
        """Return whether the chunks table is reachable."""
        try:
            with connect_postgres(self.database_url) as connection:
                connection.execute("SELECT 1 FROM chunks LIMIT 1").fetchall()
            return True
        except Exception:  # noqa: BLE001
            return False
