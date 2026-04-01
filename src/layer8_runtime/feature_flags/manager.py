"""Feature flag runtime for Phase 6 advanced retrieval features."""

from __future__ import annotations

import random
from collections.abc import Callable, Iterable, Mapping

from src.layer1_contracts.schemas.feature_flags import BenchmarkResult, FeatureFlag, FeatureStatus
from src.layer8_runtime.feature_flags.flags import DEFAULT_FEATURE_FLAGS
from src.layer8_runtime.feature_flags.gates import BenchmarkGates


class FeatureFlagManager:
    """Manage advanced feature rollout, experiments, and benchmark gates."""

    def __init__(
        self,
        flags: Iterable[FeatureFlag] | None = None,
        random_fn: Callable[[], float] | None = None,
        gates: BenchmarkGates | None = None,
    ) -> None:
        self._flags: dict[str, FeatureFlag] = {}
        self._random_fn = random_fn or random.random
        self._gates = gates or BenchmarkGates()
        self.register_many(flags or DEFAULT_FEATURE_FLAGS)

    def register(self, flag: FeatureFlag) -> None:
        """Register or replace a feature flag definition."""
        self._flags[flag.name] = flag.model_copy(deep=True)

    def register_many(self, flags: Iterable[FeatureFlag]) -> None:
        """Register multiple feature flags."""
        for flag in flags:
            self.register(flag)

    def load_from_mapping(self, config: Mapping[str, Mapping[str, object]]) -> None:
        """Load feature flag definitions from a YAML-like mapping."""
        for name, raw in config.items():
            payload = {"name": name, **dict(raw)}
            self.register(FeatureFlag.model_validate(payload))

    def get_flag(self, name: str) -> FeatureFlag | None:
        """Return a defensive copy of the requested flag."""
        flag = self._flags.get(name)
        return flag.model_copy(deep=True) if flag is not None else None

    def all_flags(self) -> list[FeatureFlag]:
        """Return all registered flags."""
        return [flag.model_copy(deep=True) for flag in self._flags.values()]

    def is_enabled(self, name: str) -> bool:
        """Return whether a feature is currently active."""
        flag = self._flags.get(name)
        if flag is None or flag.status == FeatureStatus.DISABLED:
            return False
        if flag.status == FeatureStatus.ENABLED:
            return True
        if flag.status == FeatureStatus.EXPERIMENT:
            return self._random_fn() * 100.0 < flag.rollout_percentage
        if flag.status == FeatureStatus.BENCHMARK_GATED:
            return (flag.last_benchmark_score or 0.0) >= (flag.benchmark_threshold or 0.0)
        return False

    def update_benchmark(self, name: str, result: BenchmarkResult) -> None:
        """Update a feature flag using the latest benchmark outcome."""
        flag = self._flags.get(name)
        if flag is None:
            return
        flag.last_benchmark_score = result.improvement_percent
        if self._gates.passes(flag, result):
            flag.status = FeatureStatus.ENABLED
