"""In-memory metrics collection."""

from __future__ import annotations

from collections import defaultdict
import time
from threading import Lock


class MetricsCollector:
    """Collect counters, gauges, and histograms for the running process."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def increment(self, name: str, value: int = 1, tags: dict[str, str] | None = None) -> None:
        """Increment a counter."""
        key = self._make_key(name, tags)
        with self._lock:
            self._counters[key] += value

    def gauge(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Set a gauge value."""
        key = self._make_key(name, tags)
        with self._lock:
            self._gauges[key] = value

    def histogram(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Record a histogram value."""
        key = self._make_key(name, tags)
        with self._lock:
            self._histograms[key].append(value)

    def timer(self, name: str, tags: dict[str, str] | None = None) -> "Timer":
        """Return a context manager that records duration to a histogram."""
        return Timer(self, name, tags)

    def get_metrics(self) -> dict:
        """Return a snapshot of all collected metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    key: self._summarize_histogram(values)
                    for key, values in self._histograms.items()
                },
            }

    def reset(self) -> None:
        """Clear all collected metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()

    @staticmethod
    def _make_key(name: str, tags: dict[str, str] | None = None) -> str:
        """Build a stable tagged metric key."""
        if not tags:
            return name
        tag_str = ",".join(f"{key}={value}" for key, value in sorted(tags.items()))
        return f"{name}{{{tag_str}}}"

    @staticmethod
    def _summarize_histogram(values: list[float]) -> dict:
        """Summarize histogram values for inspection and export."""
        if not values:
            return {}
        sorted_values = sorted(values)
        count = len(sorted_values)
        return {
            "count": count,
            "sum": sum(sorted_values),
            "avg": sum(sorted_values) / float(count),
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "p50": sorted_values[min(count - 1, count // 2)],
            "p95": sorted_values[min(count - 1, int((count - 1) * 0.95))],
            "p99": sorted_values[min(count - 1, int((count - 1) * 0.99))],
        }


class Timer:
    """Context manager for recording operation timing."""

    def __init__(self, collector: MetricsCollector, name: str, tags: dict[str, str] | None) -> None:
        self.collector = collector
        self.name = name
        self.tags = tags
        self.start = 0.0

    def __enter__(self) -> "Timer":
        """Start timing."""
        self.start = time.perf_counter()
        return self

    def __exit__(self, *_args) -> None:
        """Record elapsed time in milliseconds."""
        duration_ms = (time.perf_counter() - self.start) * 1000.0
        self.collector.histogram(self.name, duration_ms, self.tags)


metrics = MetricsCollector()
