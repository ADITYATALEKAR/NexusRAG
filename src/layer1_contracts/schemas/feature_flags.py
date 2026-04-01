"""Feature flag and benchmark contracts for advanced retrieval."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class FeatureStatus(str, Enum):
    """Lifecycle states for advanced Phase 6 features."""

    DISABLED = "disabled"
    ENABLED = "enabled"
    EXPERIMENT = "experiment"
    BENCHMARK_GATED = "benchmark_gated"


class FeatureFlag(BaseModel):
    """Configuration and benchmark metadata for one feature flag."""

    model_config = ConfigDict(extra="forbid")

    name: str
    status: FeatureStatus = FeatureStatus.DISABLED
    rollout_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    benchmark_threshold: float | None = None
    last_benchmark_score: float | None = None


class BenchmarkResult(BaseModel):
    """Outcome of benchmarking an advanced retrieval feature."""

    model_config = ConfigDict(extra="forbid")

    feature_name: str
    baseline_score: float
    feature_score: float
    improvement_percent: float
    passed_gate: bool
