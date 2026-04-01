"""Unit tests for safe SQL generation."""

from __future__ import annotations

from src.layer1_contracts.schemas.structured import StructuredQuery, StructuredQueryType
from src.layer2_domain.structured_retrieval.sql_generator import SafeSQLGenerator


def test_sql_generator_builds_safe_aggregation_query() -> None:
    """Aggregation queries should generate safe SELECT-only SQL."""
    generator = SafeSQLGenerator(
        allowed_tables=["documents"],
        table_schemas={"documents": ["document_id", "document_title", "document_type", "trust_score"]},
    )

    generated = generator.generate(
        StructuredQuery(
            id="query-1",
            natural_query="How many documents are there?",
            query_type=StructuredQueryType.AGGREGATION,
            target_table="documents",
            aggregations=["COUNT(*)"],
        )
    )

    assert generated.is_safe is True
    assert generated.sql == "SELECT COUNT(*) FROM documents"


def test_sql_generator_parameterizes_filters() -> None:
    """Potentially dangerous filter values should be kept in bound parameters."""
    generator = SafeSQLGenerator(
        allowed_tables=["documents"],
        table_schemas={"documents": ["document_title", "document_type", "trust_score"]},
    )

    generated = generator.generate(
        StructuredQuery(
            id="query-2",
            natural_query='Show documents for "x"; DROP TABLE documents;--',
            query_type=StructuredQueryType.FILTER,
            target_table="documents",
            columns=["document_title"],
            filters={"document_title": "x'; DROP TABLE documents;--"},
        )
    )

    assert generated.is_safe is True
    assert "DROP TABLE" not in generated.sql
    assert generated.parameters == {"p0": "x'; DROP TABLE documents;--"}


def test_sql_generator_rejects_disallowed_tables() -> None:
    """Queries against non-allowlisted tables should be rejected."""
    generator = SafeSQLGenerator(
        allowed_tables=["documents"],
        table_schemas={"documents": ["document_id"]},
    )

    generated = generator.generate(
        StructuredQuery(
            id="query-3",
            natural_query="Show users",
            query_type=StructuredQueryType.LOOKUP,
            target_table="users",
        )
    )

    assert generated.is_safe is False
    assert generated.sql == ""
