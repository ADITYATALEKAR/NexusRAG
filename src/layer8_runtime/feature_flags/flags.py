"""Default Phase 6 feature flag definitions."""

from __future__ import annotations

from src.layer1_contracts.schemas.feature_flags import FeatureFlag, FeatureStatus

CONTEXTUAL_INDEXING = FeatureFlag(
    name="contextual_indexing",
    status=FeatureStatus.BENCHMARK_GATED,
    benchmark_threshold=5.0,
)
GRAPH_RETRIEVAL = FeatureFlag(
    name="graph_retrieval",
    status=FeatureStatus.EXPERIMENT,
    rollout_percentage=10.0,
)
VECTOR_COMPRESSION = FeatureFlag(
    name="vector_compression",
    status=FeatureStatus.DISABLED,
)

DEFAULT_FEATURE_FLAGS = (
    CONTEXTUAL_INDEXING,
    GRAPH_RETRIEVAL,
    VECTOR_COMPRESSION,
)
