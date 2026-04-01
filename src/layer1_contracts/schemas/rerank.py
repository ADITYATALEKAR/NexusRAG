"""Reranking contracts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RerankRequest(BaseModel):
    """Rerank request."""

    model_config = ConfigDict(extra="forbid")

    id: str
    query: str
    documents: list[str] = Field(..., min_length=1)
    top_k: int = Field(default=10, ge=1)
    model: str | None = None


class RerankResult(BaseModel):
    """Rerank response."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    scores: list[float]
    rankings: list[int]
    model: str
    latency_ms: int
