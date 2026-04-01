"""Unit tests for Phase 7 observability services."""

from __future__ import annotations

import json

from src.layer5_wiring.observability.cost_tracker import cost_tracker
from src.layer5_wiring.observability.logging import StructuredLogger, request_id_var, trace_id_var
from src.layer5_wiring.observability.metrics import MetricsCollector
from src.layer5_wiring.observability.tracing import tracer


def test_structured_logger_includes_request_and_trace_context(capsys) -> None:
    """Structured logs should include request and trace correlation fields."""
    request_id_var.set("req-123")
    trace_id_var.set("trace-456")

    StructuredLogger(service_name="vectorcore").info(
        "phase7_log",
        component="api",
        operation="test",
    )
    captured = capsys.readouterr().out.strip()
    payload = json.loads(captured)

    assert payload["request_id"] == "req-123"
    assert payload["trace_id"] == "trace-456"
    assert payload["service"] == "vectorcore"


def test_metrics_collector_tracks_and_summarizes_values() -> None:
    """Metrics collector should track counters, gauges, and histograms."""
    collector = MetricsCollector()
    collector.increment("requests_total", tags={"status": "200"})
    collector.gauge("queue_depth", 3.0)
    collector.histogram("latency_ms", 10.0)
    collector.histogram("latency_ms", 30.0)

    snapshot = collector.get_metrics()

    assert snapshot["counters"]["requests_total{status=200}"] == 1
    assert snapshot["gauges"]["queue_depth"] == 3.0
    assert snapshot["histograms"]["latency_ms"]["avg"] == 20.0


def test_tracing_manager_keeps_parent_child_relationships() -> None:
    """Tracing should capture parent-child span relationships."""
    tracer.clear()
    with tracer.span("root") as root:
        with tracer.span("child") as child:
            assert child.parent_span_id == root.span_id

    exported = tracer.export_spans()

    assert len(exported) == 2
    assert exported[0]["operation"] == "child"
    assert exported[1]["operation"] == "root"
    assert exported[0]["parent_span_id"] == exported[1]["span_id"]


def test_cost_tracker_records_and_aggregates_costs() -> None:
    """Cost tracker should compute per-model and total costs."""
    cost_tracker.clear()
    cost_tracker.record("req-1", "openai", "gpt-4o-mini", 1000, 500)
    cost_tracker.record("req-2", "openai", "gpt-4o-mini", 1000, 500)

    assert cost_tracker.get_total_cost() > 0.0
    by_model = cost_tracker.get_cost_by_model()
    assert "gpt-4o-mini" in by_model
    assert by_model["gpt-4o-mini"] == cost_tracker.get_total_cost()
