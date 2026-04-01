"""Embedding contracts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EmbeddingRequest(BaseModel):
    """Embedding request."""

    model_config = ConfigDict(extra="forbid")

    id: str
    texts: list[str] = Field(..., min_length=1)
    model: str | None = None
    timeout_seconds: float = Field(default=30.0, gt=0)


class EmbeddingResult(BaseModel):
    """Embedding response."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    embeddings: list[list[float]]
    model: str
    dimensions: int
    total_tokens: int
    latency_ms: int
