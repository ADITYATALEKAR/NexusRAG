"""pgvector-backed vector store adapter for Neon Postgres."""

from __future__ import annotations

import json

from src.layer1_contracts.interfaces.vector_store import VectorStoreInterface
from src.layer4_providers.stores.postgres.connection import connect_postgres, vector_literal


class PostgresVectorStore(VectorStoreInterface):
    """Vector storage implemented with pgvector."""

    def __init__(
        self,
        database_url: str,
        dimensions: int = 384,
    ) -> None:
        self.database_url = database_url
        self.dimensions = dimensions

    async def insert(
        self,
        ids: list[str],
        vectors: list[list[float]],
        metadata: list[dict] | None = None,
    ) -> int:
        """Insert vectors for the supplied chunk ids."""
        with connect_postgres(self.database_url) as connection:
            for index, (chunk_id, vector) in enumerate(zip(ids, vectors)):
                payload = metadata[index] if metadata else {}
                connection.execute(
                    """
                    INSERT INTO chunk_vectors (chunk_id, embedding, payload)
                    VALUES (%s, %s::vector, %s::jsonb)
                    ON CONFLICT (chunk_id) DO UPDATE SET
                        embedding = EXCLUDED.embedding,
                        payload = EXCLUDED.payload
                    """,
                    (chunk_id, vector_literal(vector), json.dumps(payload)),
                )
        return len(ids)

    async def upsert(
        self,
        ids: list[str],
        vectors: list[list[float]],
        metadata: list[dict] | None = None,
    ) -> int:
        """Insert or update vectors."""
        return await self.insert(ids, vectors, metadata)

    async def delete(self, ids: list[str]) -> int:
        """Delete vectors by chunk id."""
        with connect_postgres(self.database_url) as connection:
            connection.execute("DELETE FROM chunk_vectors WHERE chunk_id = ANY(%s)", (ids,))
        return len(ids)

    async def search(
        self,
        query_vector: list[float],
        top_k: int = 10,
        filter: dict | None = None,
    ) -> list[tuple[str, float, dict | None]]:
        """Search for nearest vectors using cosine distance."""
        filter_sql = ""
        params: list[object] = [vector_literal(query_vector)]
        if filter and "document_id" in filter:
            filter_sql = "WHERE c.document_id = %s"
            params.append(filter["document_id"])
        params.append(top_k)
        with connect_postgres(self.database_url) as connection:
            query_params = [params[0]]
            if len(params) == 3:
                query_params.append(params[1])
            query_params.extend([params[0], params[-1]])
            rows = connection.execute(
                f"""
                SELECT
                    v.chunk_id,
                    1 - (v.embedding <=> %s::vector) AS score,
                    jsonb_build_object(
                        'document_id', c.document_id,
                        'document_title', c.document_title,
                        'document_type', c.document_type,
                        'section_title', c.section_title,
                        'page_numbers', c.page_numbers,
                        'tags', c.tags,
                        'trust_score', c.trust_score
                    ) AS payload
                FROM chunk_vectors v
                JOIN chunks c ON c.id = v.chunk_id
                {filter_sql}
                ORDER BY v.embedding <=> %s::vector
                LIMIT %s
                """,
                tuple(query_params),
            ).fetchall()
        return [(row["chunk_id"], float(row["score"]), row["payload"]) for row in rows]

    async def fetch(self, ids: list[str]) -> list[tuple[str, list[float], dict | None]]:
        """Fetch vectors by chunk id."""
        with connect_postgres(self.database_url) as connection:
            rows = connection.execute(
                """
                SELECT chunk_id, embedding::text AS embedding, payload
                FROM chunk_vectors
                WHERE chunk_id = ANY(%s)
                ORDER BY chunk_id ASC
                """,
                (ids,),
            ).fetchall()
        return [
            (
                row["chunk_id"],
                _parse_vector_text(row["embedding"]),
                row["payload"],
            )
            for row in rows
        ]

    async def health_check(self) -> bool:
        """Return whether the vector tables are reachable."""
        try:
            with connect_postgres(self.database_url) as connection:
                connection.execute("SELECT 1 FROM chunk_vectors LIMIT 1").fetchall()
            return True
        except Exception:  # noqa: BLE001
            return False

    async def collection_exists(self, name: str) -> bool:
        """Mirror the collection interface with the Postgres vector table."""
        return name == "chunk_vectors"

    async def count(self) -> int:
        """Return the number of stored vectors."""
        with connect_postgres(self.database_url) as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM chunk_vectors").fetchone()
        return int(row["count"] if row else 0)


def _parse_vector_text(value: str) -> list[float]:
    """Convert pgvector text output into a Python list."""
    trimmed = value.strip()[1:-1]
    if not trimmed:
        return []
    return [float(item) for item in trimmed.split(",")]
