"""Benchmark gate helpers for advanced retrieval features."""

from __future__ import annotations

from src.layer1_contracts.schemas.feature_flags import BenchmarkResult, FeatureFlag


class BenchmarkGates:
    """Evaluate whether benchmark results clear rollout gates."""

    def evaluate(
        self,
        feature_name: str,
        baseline_score: float,
        feature_score: float,
        threshold: float,
    ) -> BenchmarkResult:
        """Return a normalized benchmark result with gate status."""
        if baseline_score == 0:
            improvement = 100.0 if feature_score > 0 else 0.0
        else:
            improvement = ((feature_score - baseline_score) / baseline_score) * 100.0
        passed_gate = improvement >= threshold and feature_score >= baseline_score
        return BenchmarkResult(
            feature_name=feature_name,
            baseline_score=baseline_score,
            feature_score=feature_score,
            improvement_percent=improvement,
            passed_gate=passed_gate,
        )

    def passes(self, flag: FeatureFlag, result: BenchmarkResult) -> bool:
        """Return whether the supplied result clears the flag threshold."""
        threshold = flag.benchmark_threshold or 0.0
        return result.improvement_percent >= threshold and result.passed_gate
