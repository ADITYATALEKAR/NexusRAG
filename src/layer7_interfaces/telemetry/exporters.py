"""Metric export helpers."""

from __future__ import annotations

import json

from src.layer5_wiring.observability.metrics import MetricsCollector


class MetricExporters:
    """Export collected metrics in multiple formats."""

    def __init__(self, collector: MetricsCollector) -> None:
        self.collector = collector

    def to_json(self) -> str:
        """Export metrics as JSON."""
        return json.dumps(self.collector.get_metrics(), indent=2, sort_keys=True)

    def to_prometheus(self) -> str:
        """Export metrics in a simple Prometheus-style text format."""
        snapshot = self.collector.get_metrics()
        lines: list[str] = []

        for name, value in snapshot["counters"].items():
            lines.append(f"{self._sanitize(name)} {value}")
        for name, value in snapshot["gauges"].items():
            lines.append(f"{self._sanitize(name)} {value}")
        for name, summary in snapshot["histograms"].items():
            safe_name = self._sanitize(name)
            for field, value in summary.items():
                lines.append(f"{safe_name}_{field} {value}")
        return "\n".join(lines)

    @staticmethod
    def _sanitize(name: str) -> str:
        """Convert metric names to Prometheus-friendly identifiers."""
        return (
            name.replace("{", "_")
            .replace("}", "")
            .replace(",", "_")
            .replace("=", "_")
            .replace("-", "_")
            .replace("/", "_")
        )
