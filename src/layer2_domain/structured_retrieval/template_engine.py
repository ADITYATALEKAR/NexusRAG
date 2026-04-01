"""Natural-language to structured-query inference."""

from __future__ import annotations

import re

from src.layer1_contracts.schemas.structured import StructuredQuery, StructuredQueryType


class QueryTemplateEngine:
    """Infer a bounded structured query from natural language."""

    COLUMN_ALIASES = {
        "title": "document_title",
        "titles": "document_title",
        "type": "document_type",
        "types": "document_type",
        "trust": "trust_score",
        "score": "trust_score",
        "created": "created_at",
        "date": "created_at",
        "chunk count": "chunk_count",
        "chunks": "chunk_count",
        "checksum": "checksum",
        "indexed": "indexed_at",
        "stale": "is_stale",
    }

    def __init__(
        self,
        templates: dict[str, object] | None,
        table_schemas: dict[str, list[str]],
        table_aliases: dict[str, str] | None = None,
        default_table: str = "documents",
    ) -> None:
        self.templates = templates or {}
        self.table_schemas = table_schemas
        self.table_aliases = table_aliases or {}
        self.default_table = default_table

    def infer(self, query_id: str, natural_query: str) -> StructuredQuery:
        """Infer the smallest safe structured query that fits the text."""
        text_lower = natural_query.lower()
        target_table = self._detect_table(text_lower)
        query_type = self._detect_type(text_lower)
        columns = self._detect_columns(text_lower, target_table)
        filters = self._detect_filters(natural_query, target_table)
        aggregations = self._detect_aggregations(text_lower)
        order_by = self._detect_order_by(text_lower, target_table)
        limit = self._detect_limit(text_lower)

        if query_type == StructuredQueryType.AGGREGATION and not aggregations:
            aggregations = ["COUNT(*)"]

        if query_type in {StructuredQueryType.LOOKUP, StructuredQueryType.FILTER, StructuredQueryType.RANKING}:
            if not columns:
                columns = ["*"]

        return StructuredQuery(
            id=query_id,
            natural_query=natural_query,
            query_type=query_type,
            target_table=target_table,
            columns=columns,
            filters=filters,
            aggregations=aggregations,
            order_by=order_by,
            limit=limit,
        )

    def _detect_type(self, text_lower: str) -> StructuredQueryType:
        if any(token in text_lower for token in ["how many", "how much", "count", "total", "average", "sum"]):
            return StructuredQueryType.AGGREGATION
        if any(token in text_lower for token in ["top ", "highest", "lowest", "rank", "order by"]):
            return StructuredQueryType.RANKING
        if any(token in text_lower for token in ["compare", "difference"]):
            return StructuredQueryType.COMPARISON
        if any(token in text_lower for token in ["where", "with", "for ", "show"]):
            return StructuredQueryType.FILTER
        return StructuredQueryType.LOOKUP

    def _detect_table(self, text_lower: str) -> str:
        for alias, table_name in self.table_aliases.items():
            if alias.lower() in text_lower:
                return table_name
        if "index" in text_lower or "stale" in text_lower or "checksum" in text_lower:
            return "index_state"
        if "chunk" in text_lower:
            return "chunk_metadata"
        return self.default_table

    def _detect_columns(self, text_lower: str, target_table: str) -> list[str]:
        available_columns = self.table_schemas.get(target_table, [])
        selected: list[str] = []
        for alias, column_name in self.COLUMN_ALIASES.items():
            if alias in text_lower and column_name in available_columns and column_name not in selected:
                selected.append(column_name)
        return selected

    def _detect_aggregations(self, text_lower: str) -> list[str]:
        aggregations: list[str] = []
        if "average" in text_lower or "avg" in text_lower:
            aggregations.append("AVG(trust_score)")
        if "sum" in text_lower:
            aggregations.append("SUM(chunk_count)")
        if any(token in text_lower for token in ["how many", "count", "total"]):
            aggregations.append("COUNT(*)")
        return aggregations

    def _detect_filters(self, natural_query: str, target_table: str) -> dict[str, object]:
        filters: dict[str, object] = {}
        text_lower = natural_query.lower()
        schema = set(self.table_schemas.get(target_table, []))

        quoted_match = re.search(r'"([^"]+)"', natural_query)
        if quoted_match and "document_title" in schema:
            filters["document_title"] = quoted_match.group(1)

        doc_type_match = re.search(r"\b(pdf|docx|txt|md|html|csv|json)\b", text_lower)
        if doc_type_match and "document_type" in schema:
            filters["document_type"] = doc_type_match.group(1)

        if "stale" in text_lower and "is_stale" in schema:
            filters["is_stale"] = 1

        trust_match = re.search(r"trust\s*(?:>=|>|at least)\s*(\d+(?:\.\d+)?)", text_lower)
        if trust_match and "trust_score" in schema:
            filters["trust_score"] = float(trust_match.group(1))

        return filters

    def _detect_order_by(self, text_lower: str, target_table: str) -> str | None:
        available_columns = set(self.table_schemas.get(target_table, []))
        if "highest trust" in text_lower and "trust_score" in available_columns:
            return "trust_score DESC"
        if "lowest trust" in text_lower and "trust_score" in available_columns:
            return "trust_score ASC"
        if "latest" in text_lower and "created_at" in available_columns:
            return "created_at DESC"
        return None

    def _detect_limit(self, text_lower: str) -> int | None:
        match = re.search(r"\btop\s+(\d+)\b", text_lower)
        if match:
            return int(match.group(1))
        if "list all" in text_lower or "show me all" in text_lower:
            return None
        return 10 if "list" in text_lower or "show" in text_lower else None
