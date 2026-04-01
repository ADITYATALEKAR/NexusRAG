"""Query contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class QueryType(str, Enum):
    """Supported query types."""

    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    STRUCTURED = "structured"
    COMPARATIVE = "comparative"
    MULTI_HOP = "multi_hop"


class QueryFilters(BaseModel):
    """Query filters."""

    model_config = ConfigDict(extra="forbid")

    document_ids: list[str] | None = None
    document_types: list[str] | None = None
    tags: list[str] | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    min_trust_score: float | None = Field(default=None, ge=0.0, le=1.0)
    exclude_chunk_ids: list[str] | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "QueryFilters":
        """Ensure date bounds are coherent."""
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise ValueError("date_to must be greater than or equal to date_from")
        return self


class QueryConfig(BaseModel):
    """Retrieval configuration for a query."""

    model_config = ConfigDict(extra="forbid")

    top_k: int = Field(default=10, ge=1, le=100)
    rerank: bool = True
    rerank_top_k: int = Field(default=25, ge=1, le=100)

    @model_validator(mode="after")
    def validate_rerank_bounds(self) -> "QueryConfig":
        """Ensure rerank_top_k is not less than top_k when reranking is enabled."""
        if self.rerank and self.rerank_top_k < self.top_k:
            raise ValueError("rerank_top_k must be >= top_k when rerank is enabled")
        return self


class Query(BaseModel):
    """User query contract."""

    model_config = ConfigDict(extra="forbid")

    id: str
    text: str = Field(..., min_length=1, max_length=10000)
    query_type: QueryType = QueryType.HYBRID
    filters: QueryFilters = Field(default_factory=QueryFilters)
    config: QueryConfig = Field(default_factory=QueryConfig)
    session_id: str | None = None
    request_id: str | None = None
    embedding: list[float] | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
