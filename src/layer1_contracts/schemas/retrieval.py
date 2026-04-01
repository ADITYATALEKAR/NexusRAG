"""Retrieval contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from src.layer1_contracts.schemas.retrieval_config import RetrievalConfig


class RetrievalSource(str, Enum):
    """Where a retrieval candidate came from."""

    DENSE = "dense"
    LEXICAL = "lexical"
    HYBRID = "hybrid"
    RERANKED = "reranked"


class RetrievalScores(BaseModel):
    """Scoring metadata for a candidate."""

    model_config = ConfigDict(extra="forbid")

    dense_score: float | None = None
    lexical_score: float | None = None
    fusion_score: float | None = None
    rerank_score: float | None = None
    final_score: float


class RetrievalCandidate(BaseModel):
    """One retrieval candidate."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    document_id: str
    content: str
    scores: RetrievalScores
    source: RetrievalSource
    rank: int = Field(..., ge=0)
    document_title: str | None = None
    section_title: str | None = None
    page_numbers: list[int] = Field(default_factory=list)


class RetrievalResult(BaseModel):
    """Aggregate retrieval result."""

    model_config = ConfigDict(extra="forbid")

    query_id: str
    candidates: list[RetrievalCandidate] = Field(default_factory=list)
    total_dense_candidates: int = 0
    total_lexical_candidates: int = 0
    total_after_fusion: int = 0
    dense_latency_ms: int | None = None
    lexical_latency_ms: int | None = None
    total_latency_ms: int | None = None
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RetrievalStageResult(BaseModel):
    """Result from a single retrieval stage."""

    model_config = ConfigDict(extra="forbid")

    stage: str
    candidates: list[RetrievalCandidate] = Field(default_factory=list)
    count: int
    latency_ms: int


class RetrievalDiagnostics(BaseModel):
    """Full diagnostics for a retrieval operation."""

    model_config = ConfigDict(extra="forbid")

    query_id: str
    query_text: str
    query_embedding_time_ms: int
    dense_result: RetrievalStageResult | None = None
    lexical_result: RetrievalStageResult | None = None
    fusion_result: RetrievalStageResult | None = None
    filter_result: RetrievalStageResult | None = None
    rerank_result: RetrievalStageResult | None = None
    final_candidates: list[RetrievalCandidate] = Field(default_factory=list)
    total_latency_ms: int
    config: RetrievalConfig


class HybridRetrievalResult(BaseModel):
    """Final hybrid retrieval output."""

    model_config = ConfigDict(extra="forbid")

    query_id: str
    candidates: list[RetrievalCandidate] = Field(default_factory=list)
    total_candidates: int
    diagnostics: RetrievalDiagnostics | None = None
    dense_latency_ms: int
    lexical_latency_ms: int
    fusion_latency_ms: int
    filter_latency_ms: int
    rerank_latency_ms: int
    total_latency_ms: int
