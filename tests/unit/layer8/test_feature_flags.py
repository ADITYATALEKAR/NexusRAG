"""Unit tests for Phase 6 feature flags and benchmark gates."""

from __future__ import annotations

from src.layer1_contracts.schemas.feature_flags import FeatureFlag, FeatureStatus
from src.layer8_runtime.feature_flags.gates import BenchmarkGates
from src.layer8_runtime.feature_flags.manager import FeatureFlagManager


def test_feature_flag_manager_defaults_are_safe() -> None:
    """Advanced features should remain off unless rollout rules enable them."""
    manager = FeatureFlagManager(random_fn=lambda: 0.99)

    assert manager.is_enabled("contextual_indexing") is False
    assert manager.is_enabled("graph_retrieval") is False
    assert manager.is_enabled("vector_compression") is False


def test_feature_flag_manager_updates_benchmark_gated_flag() -> None:
    """Passing a benchmark gate should enable the feature."""
    manager = FeatureFlagManager(
        flags=[
            FeatureFlag(
                name="contextual_indexing",
                status=FeatureStatus.BENCHMARK_GATED,
                benchmark_threshold=5.0,
            )
        ]
    )
    result = BenchmarkGates().evaluate(
        feature_name="contextual_indexing",
        baseline_score=0.50,
        feature_score=0.53,
        threshold=5.0,
    )

    manager.update_benchmark("contextual_indexing", result)

    assert result.passed_gate is True
    assert manager.is_enabled("contextual_indexing") is True


def test_experiment_flag_respects_rollout_percentage() -> None:
    """Experiment flags should honor rollout percentages deterministically."""
    manager = FeatureFlagManager(
        flags=[
            FeatureFlag(
                name="graph_retrieval",
                status=FeatureStatus.EXPERIMENT,
                rollout_percentage=10.0,
            )
        ],
        random_fn=lambda: 0.05,
    )

    assert manager.is_enabled("graph_retrieval") is True
