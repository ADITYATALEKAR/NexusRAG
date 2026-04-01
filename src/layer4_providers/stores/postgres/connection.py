"""Shared Postgres helpers for Neon-backed runtime services."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

import psycopg
from psycopg.rows import dict_row

from src.layer1_contracts.interfaces.sql_executor import SQLExecutorInterface


def connect_postgres(database_url: str) -> psycopg.Connection:
    """Create a Postgres connection suitable for short-lived request work."""
    connection = psycopg.connect(database_url, row_factory=dict_row, autocommit=True)
    return connection


def vector_literal(values: list[float]) -> str:
    """Serialize one embedding into pgvector literal format."""
    return "[" + ",".join(f"{value:.8f}" for value in values) + "]"


class PostgresSQLExecutor(SQLExecutorInterface):
    """Thin readonly SQL executor for structured retrieval over Postgres."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    @contextmanager
    def connection(self) -> Iterator[psycopg.Connection]:
        """Yield a short-lived autocommit connection."""
        connection = connect_postgres(self.database_url)
        try:
            yield connection
        finally:
            connection.close()

    def execute(self, sql: str, parameters: list[Any] | tuple[Any, ...]) -> Any:
        """Execute one readonly SQL statement and return a cursor."""
        connection = connect_postgres(self.database_url)
        try:
            cursor = connection.execute(sql, parameters)
            rows = cursor.fetchall() if cursor.description else []
            return _BufferedCursor(rows=rows, description=cursor.description)
        finally:
            connection.close()

    def ensure_supporting_views(self) -> None:
        """Create readonly compatibility views used by structured retrieval."""
        with self.connection() as connection:
            connection.execute(
                """
                CREATE VIEW IF NOT EXISTS documents_view AS
                SELECT
                    d.id AS document_id,
                    d.title AS document_title,
                    d.document_type,
                    d.tags,
                    d.trust_score,
                    d.ingested_at AS created_at,
                    COUNT(c.id) AS chunk_count
                FROM documents d
                LEFT JOIN chunks c ON c.document_id = d.id
                GROUP BY d.id, d.title, d.document_type, d.tags, d.trust_score, d.ingested_at
                """
            )


class _BufferedCursor:
    """Simple cursor-like object backed by eagerly fetched rows."""

    def __init__(self, rows: list[dict[str, Any]], description: Any) -> None:
        self._rows = rows
        self.description = description

    def fetchall(self) -> list[dict[str, Any]]:
        """Return all fetched rows."""
        return self._rows
