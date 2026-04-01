"""Metrics and telemetry routes."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter

from src.layer5_wiring.observability.cost_tracker import cost_tracker
from src.layer5_wiring.observability.metrics import metrics
from src.layer5_wiring.observability.tracing import tracer
from src.layer7_interfaces.telemetry.exporters import MetricExporters

router = APIRouter()


@router.get("/metrics")
async def get_metrics() -> dict:
    """Return current in-memory metrics."""
    return metrics.get_metrics()


@router.get("/metrics/prometheus")
async def get_metrics_prometheus() -> dict[str, str]:
    """Return a Prometheus-style text export."""
    return {"metrics": MetricExporters(metrics).to_prometheus()}


@router.get("/traces")
async def get_traces(limit: int = 100) -> list[dict]:
    """Return captured spans."""
    return tracer.export_spans(limit=limit)


@router.get("/costs")
async def get_costs(hours: int = 24) -> dict:
    """Return cost totals for the requested lookback window."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    return {
        "total_usd": cost_tracker.get_total_cost(since),
        "by_model": cost_tracker.get_cost_by_model(since),
    }
