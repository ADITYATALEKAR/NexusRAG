"""Typed SDK response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Citation(BaseModel):
    """SDK citation model."""

    model_config = ConfigDict(extra="allow")

    citation_key: str
    chunk_id: str
    document_id: str
    document_title: str | None = None
    page_numbers: list[int] = Field(default_factory=list)
    quoted_text: str | None = None


class QueryResult(BaseModel):
    """SDK answer model."""

    model_config = ConfigDict(extra="allow")

    answer_id: str
    query_id: str
    text: str
    status: str
    citations: list[Citation] = Field(default_factory=list)
    trace: dict[str, Any] | None = None

    @property
    def answer(self) -> str:
        """Backward-compatible alias used by the CLI prompt."""
        return self.text


class IngestResult(BaseModel):
    """SDK ingestion model."""

    model_config = ConfigDict(extra="allow")

    request_id: str
    document_id: str
    status: str
    parser_used: str
    parser_confidence: float
    chunks_indexed: int
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    processing_time_ms: int
    indexing_job_id: str


class EvalResult(BaseModel):
    """SDK evaluation result model."""

    model_config = ConfigDict(extra="allow")

    run_id: str
    dataset_id: str
    retrieval_metrics: dict[str, Any]
    generation_metrics: dict[str, Any]
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    total_cost_usd: float
    evaluated_at: datetime | None = None


class RegressionTestResult(BaseModel):
    """SDK regression test result model."""

    model_config = ConfigDict(extra="allow")

    current: EvalResult
    baseline: EvalResult
    regressions: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    passed: bool
