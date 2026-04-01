"""Evaluation contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MetricType(str, Enum):
    """Supported evaluation metric families."""

    RETRIEVAL = "retrieval"
    GENERATION = "generation"
    END_TO_END = "end_to_end"
    LATENCY = "latency"
    COST = "cost"


class EvalDatasetItem(BaseModel):
    """One golden evaluation item."""

    model_config = ConfigDict(extra="forbid")

    id: str
    query: str
    expected_chunks: list[str] = Field(default_factory=list)
    expected_answer: str | None = None
    expected_citations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvalDataset(BaseModel):
    """Versioned dataset for retrieval and generation evaluation."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    version: str
    items: list[EvalDatasetItem]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RetrievalMetricsResult(BaseModel):
    """Aggregate retrieval quality metrics."""

    model_config = ConfigDict(extra="forbid")

    precision_at_k: dict[int, float]
    recall_at_k: dict[int, float]
    mrr: float
    ndcg_at_k: dict[int, float]
    map_score: float
    hit_rate_at_k: dict[int, float]


class GenerationMetricsResult(BaseModel):
    """Aggregate answer quality metrics."""

    model_config = ConfigDict(extra="forbid")

    faithfulness: float
    relevance: float
    citation_precision: float
    citation_recall: float
    answer_similarity: float
    abstention_accuracy: float


class EvalRunResult(BaseModel):
    """Result of evaluating one dataset against the live system."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    dataset_id: str
    retrieval_metrics: RetrievalMetricsResult
    generation_metrics: GenerationMetricsResult
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    total_cost_usd: float
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RegressionResult(BaseModel):
    """Comparison between a fresh run and a stored baseline."""

    model_config = ConfigDict(extra="forbid")

    current: EvalRunResult
    baseline: EvalRunResult
    regressions: list[str]
    improvements: list[str]
    passed: bool
