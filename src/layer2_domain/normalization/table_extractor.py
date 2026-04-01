"""Table normalization helpers."""

from __future__ import annotations

from src.layer1_contracts.schemas.parsing import ParseResult


class TableExtractor:
    """Normalize parser-emitted table metadata."""

    def extract(self, parse_result: ParseResult) -> list[dict]:
        """Return normalized table metadata."""
        tables: list[dict] = []
        for index, table in enumerate(parse_result.tables):
            normalized = dict(table)
            normalized.setdefault("id", f"table-{index}")
            tables.append(normalized)
        return tables
