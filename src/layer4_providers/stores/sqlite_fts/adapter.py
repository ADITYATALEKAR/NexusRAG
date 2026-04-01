"""SQLite FTS lexical store adapter."""

from __future__ import annotations

from pathlib import Path
import sqlite3

from src.layer1_contracts.interfaces.lexical_store import LexicalStoreInterface


class SQLiteFTSAdapter(LexicalStoreInterface):
    """Lexical store adapter backed by SQLite FTS5."""

    def __init__(self, db_path: str = "data/lexical.db") -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    async def index(self, id: str, content: str, metadata: dict | None = None) -> None:
        """Index a chunk into the FTS table."""
        meta = metadata or {}
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO chunks_fts (chunk_id, content, document_id, section_title)
                VALUES (?, ?, ?, ?)
                """,
                (id, content, meta.get("document_id", ""), meta.get("section_title", "")),
            )
            connection.commit()

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter: dict | None = None,
    ) -> list[tuple[str, float]]:
        """Search indexed content using BM25."""
        if not query.strip():
            return []

        sql = """
            SELECT chunk_id, bm25(chunks_fts) as score
            FROM chunks_fts
            WHERE chunks_fts MATCH ?
        """
        params: list = [query]
        if filter and "document_id" in filter:
            sql += " AND document_id = ?"
            params.append(filter["document_id"])
        sql += " ORDER BY score LIMIT ?"
        params.append(top_k)

        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.execute(sql, params)
            return [(row[0], -row[1]) for row in cursor.fetchall()]

    async def delete(self, id: str) -> bool:
        """Delete one chunk from the lexical index."""
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.execute("DELETE FROM chunks_fts WHERE chunk_id = ?", (id,))
            connection.commit()
            return cursor.rowcount > 0

    async def health_check(self) -> bool:
        """Return whether the lexical store is healthy."""
        try:
            with sqlite3.connect(self.db_path) as connection:
                connection.execute("SELECT 1 FROM chunks_fts LIMIT 1")
            return True
        except Exception:  # noqa: BLE001
            return False

    def _init_db(self) -> None:
        """Create the FTS table if it does not already exist."""
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    chunk_id,
                    content,
                    document_id,
                    section_title,
                    tokenize='porter unicode61'
                )
                """
            )
            connection.commit()
