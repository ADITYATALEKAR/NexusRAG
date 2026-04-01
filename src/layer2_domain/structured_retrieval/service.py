"""Structured retrieval execution service."""

from __future__ import annotations

from datetime import datetime, timezone
import sqlite3
from typing import Any

from src.layer1_contracts.schemas.structured import StructuredQuery, StructuredResult
from src.layer2_domain.structured_retrieval.result_formatter import StructuredResultFormatter
from src.layer2_domain.structured_retrieval.sql_generator import SafeSQLGenerator
from src.layer2_domain.structured_retrieval.template_engine import QueryTemplateEngine


class StructuredRetrievalService:
    """Execute structured queries against bounded tabular data."""

    def __init__(
        self,
        sql_generator: SafeSQLGenerator,
        db_connection: Any,
        result_formatter: StructuredResultFormatter,
        template_engine: QueryTemplateEngine | None = None,
    ) -> None:
        self.sql_generator = sql_generator
        self.db = db_connection
        self.formatter = result_formatter
        self.template_engine = template_engine
        self._ensure_supporting_views()

    def build_query(self, query_id: str, natural_query: str) -> StructuredQuery:
        """Infer a bounded structured query from text."""
        if self.template_engine is None:
            raise ValueError("Structured retrieval template engine is not configured")
        return self.template_engine.infer(query_id, natural_query)

    async def execute(self, structured_query: StructuredQuery) -> StructuredResult:
        """Execute a structured query and return rows plus a formatted answer."""
        start = datetime.now(timezone.utc)
        generated = self.sql_generator.generate(structured_query)
        if not generated.is_safe:
            return StructuredResult(
                query_id=structured_query.id,
                rows=[],
                columns=[],
                row_count=0,
                execution_time_ms=0,
                formatted_answer=f"Query rejected: {', '.join(generated.safety_warnings)}",
            )

        try:
            cursor = self.db.execute(generated.sql, generated.parameters)
            columns = [description[0] for description in cursor.description] if cursor.description else []
            rows = [dict(row) if isinstance(row, sqlite3.Row) else dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as error:  # noqa: BLE001
            return StructuredResult(
                query_id=structured_query.id,
                rows=[],
                columns=[],
                row_count=0,
                execution_time_ms=0,
                formatted_answer=f"Query execution failed: {error}",
            )

        elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
        formatted = self.formatter.format(structured_query.natural_query, rows, columns)
        return StructuredResult(
            query_id=structured_query.id,
            rows=rows,
            columns=columns,
            row_count=len(rows),
            execution_time_ms=elapsed,
            formatted_answer=formatted,
        )

    def _ensure_supporting_views(self) -> None:
        """Expose a document-level view on top of chunk metadata when available."""
        try:
            existing_objects = {
                row[0]
                for row in self.db.execute(
                    "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
                ).fetchall()
            }
            if "documents" in existing_objects:
                return
            if "chunk_metadata" not in existing_objects:
                return
            self.db.execute(
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
            self.db.commit()
        except Exception:  # noqa: BLE001
            pass
