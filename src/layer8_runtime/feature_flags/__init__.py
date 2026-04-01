"""Phase 6 feature flag runtime exports."""

from src.layer8_runtime.feature_flags.flags import (
    CONTEXTUAL_INDEXING,
    DEFAULT_FEATURE_FLAGS,
    GRAPH_RETRIEVAL,
    VECTOR_COMPRESSION,
)
from src.layer8_runtime.feature_flags.gates import BenchmarkGates
from src.layer8_runtime.feature_flags.manager import FeatureFlagManager

__all__ = [
    "BenchmarkGates",
    "CONTEXTUAL_INDEXING",
    "DEFAULT_FEATURE_FLAGS",
    "FeatureFlagManager",
    "GRAPH_RETRIEVAL",
    "VECTOR_COMPRESSION",
]
