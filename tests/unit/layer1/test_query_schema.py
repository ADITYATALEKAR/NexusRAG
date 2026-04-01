"""Tests for the query schema."""

import pytest
from pydantic import ValidationError

from src.layer1_contracts.schemas.query import Query, QueryConfig


def test_query_schema_accepts_valid_payload() -> None:
    """A valid query payload should parse."""
    query = Query(id="query-1", text="What is VectorCore?")

    assert query.config.top_k == 10


def test_query_config_rejects_invalid_rerank_bounds() -> None:
    """rerank_top_k cannot be below top_k when reranking is enabled."""
    with pytest.raises(ValidationError):
        QueryConfig(top_k=20, rerank=True, rerank_top_k=10)
