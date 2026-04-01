"""Integration tests for Phase 7 evaluation routes and telemetry middleware."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.middleware.logging import RequestLoggingMiddleware
from apps.api.middleware.metrics import MetricsMiddleware
from apps.api.middleware.tracing import TracingMiddleware
from apps.api.routes.eval import router as eval_router
from apps.api.routes.metrics import router as metrics_router
from src.layer1_contracts.schemas.evaluation import (
    EvalDataset,
    EvalDatasetItem,
    EvalRunResult,
    GenerationMetricsResult,
    RetrievalMetricsResult,
)
from src.layer5_wiring.observability.cost_tracker import cost_tracker
from src.layer5_wiring.observability.metrics import metrics
from src.layer5_wiring.observability.tracing import tracer


class StubDatasetManager:
    """Dataset manager stub for eval route integration tests."""

    def load(self, dataset_id: str) -> EvalDataset:
        return EvalDataset(
            id=dataset_id,
            name="stub",
            version="1.0",
            items=[EvalDatasetItem(id="item-1", query="What is VectorCore?")],
        )


class StubEvalService:
    """Evaluation service stub for route tests."""

    async def evaluate_dataset(self, dataset: EvalDataset, use_ragas: bool = False) -> EvalRunResult:
        del use_ragas
        return EvalRunResult(
            run_id="eval-1",
            dataset_id=dataset.id,
            retrieval_metrics=RetrievalMetricsResult(
                precision_at_k={1: 1.0, 3: 1.0, 5: 1.0, 10: 1.0},
                recall_at_k={1: 1.0, 3: 1.0, 5: 1.0, 10: 1.0},
                mrr=1.0,
                ndcg_at_k={1: 1.0, 3: 1.0, 5: 1.0, 10: 1.0},
                map_score=1.0,
                hit_rate_at_k={1: 1.0, 3: 1.0, 5: 1.0, 10: 1.0},
            ),
            generation_metrics=GenerationMetricsResult(
                faithfulness=1.0,
                relevance=1.0,
                citation_precision=1.0,
                citation_recall=1.0,
                answer_similarity=1.0,
                abstention_accuracy=1.0,
            ),
            avg_latency_ms=10.0,
            p95_latency_ms=10.0,
            p99_latency_ms=10.0,
            total_cost_usd=0.01,
            evaluated_at=datetime.now(timezone.utc),
        )


class StubRegressionRunner:
    """Regression runner stub for route tests."""

    async def run(self, dataset: EvalDataset, baseline_id: str):  # noqa: ARG002
        return {
            "current": await StubEvalService().evaluate_dataset(dataset),
            "baseline": await StubEvalService().evaluate_dataset(dataset),
            "regressions": [],
            "improvements": [],
            "passed": True,
        }

    def save_baseline(self, result: EvalRunResult, baseline_id: str):  # noqa: ARG002
        return "saved.json"


@dataclass
class StubEvaluationRuntime:
    """Evaluation runtime stub placed onto app state."""

    dataset_manager: StubDatasetManager
    eval_service: StubEvalService
    regression_runner: StubRegressionRunner
    default_use_ragas: bool = False


def test_eval_routes_and_telemetry_endpoints_work_together() -> None:
    """Eval routes, telemetry middleware, and metrics endpoints should work together."""
    metrics.reset()
    tracer.clear()
    cost_tracker.clear()
    cost_tracker.record("req-1", "openai", "gpt-4o-mini", 1000, 500)

    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(TracingMiddleware)
    app.include_router(eval_router, prefix="/eval")
    app.include_router(metrics_router)
    app.state.evaluation_runtime = StubEvaluationRuntime(
        dataset_manager=StubDatasetManager(),
        eval_service=StubEvalService(),
        regression_runner=StubRegressionRunner(),
    )

    @app.get("/ping")
    async def ping() -> dict[str, str]:
        return {"status": "ok"}

    with TestClient(app) as client:
        eval_response = client.post("/eval/evaluate", params={"dataset_id": "vectorcore_smoke"})
        assert eval_response.status_code == 200
        assert eval_response.json()["dataset_id"] == "vectorcore_smoke"

        ping_response = client.get("/ping")
        assert ping_response.status_code == 200
        assert ping_response.headers["X-Request-ID"]
        assert ping_response.headers["X-Trace-ID"]

        metrics_response = client.get("/metrics")
        assert metrics_response.status_code == 200
        assert metrics_response.json()["counters"]

        traces_response = client.get("/traces")
        assert traces_response.status_code == 200
        assert len(traces_response.json()) >= 2

        costs_response = client.get("/costs")
        assert costs_response.status_code == 200
        assert costs_response.json()["total_usd"] > 0.0
