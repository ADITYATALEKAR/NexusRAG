"""Evaluation routes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, status

from apps.api.routes.answer import _get_or_build_answer_runtime
from src.layer0_core.ids.base import RequestId
from src.layer1_contracts.schemas.evaluation import EvalRunResult, RegressionResult
from src.layer2_domain.evaluation.dataset_manager import GoldenDatasetManager
from src.layer2_domain.evaluation.generation_metrics import GenerationMetrics
from src.layer2_domain.evaluation.ragas_adapter import RAGASAdapter
from src.layer2_domain.evaluation.regression import RegressionTestRunner
from src.layer2_domain.evaluation.retrieval_metrics import RetrievalMetrics
from src.layer2_domain.evaluation.service import EvaluationService
from src.layer8_runtime.config.loader import ConfigLoader

router = APIRouter()


@dataclass
class EvaluationRuntime:
    """Lazy Phase 7 evaluation runtime."""

    dataset_manager: GoldenDatasetManager
    eval_service: EvaluationService
    regression_runner: RegressionTestRunner
    default_use_ragas: bool


@router.post("/evaluate", response_model=EvalRunResult)
async def evaluate(dataset_id: str, request: Request, use_ragas: bool | None = None) -> EvalRunResult:
    """Evaluate a golden dataset against the live answer runtime."""
    runtime = await _get_or_build_eval_runtime(request)
    dataset = runtime.dataset_manager.load(dataset_id)
    return await runtime.eval_service.evaluate_dataset(
        dataset,
        use_ragas=runtime.default_use_ragas if use_ragas is None else use_ragas,
    )


@router.post("/regression", response_model=RegressionResult)
async def regression_test(dataset_id: str, baseline_id: str, request: Request) -> RegressionResult:
    """Run regression testing against a stored baseline."""
    runtime = await _get_or_build_eval_runtime(request)
    dataset = runtime.dataset_manager.load(dataset_id)
    return await runtime.regression_runner.run(dataset, baseline_id)


@router.post("/baseline")
async def save_baseline(result: EvalRunResult, baseline_id: str, request: Request) -> dict:
    """Persist an evaluation result as a regression baseline."""
    runtime = await _get_or_build_eval_runtime(request)
    path = runtime.regression_runner.save_baseline(result, baseline_id)
    return {"status": "saved", "path": str(path)}


async def _get_or_build_eval_runtime(request: Request) -> EvaluationRuntime:
    """Return the cached evaluation runtime or lazily build it."""
    runtime = getattr(request.app.state, "evaluation_runtime", None)
    if runtime is not None:
        return runtime

    config_dir = Path(__file__).resolve().parents[3] / "configs"
    loader = ConfigLoader(config_dir=config_dir)
    raw_config = loader.load_yaml("evaluation/evaluation.yaml").get("evaluation", {})
    answer_runtime = await _get_or_build_answer_runtime(request)

    embedder = _resolve_embedder(answer_runtime.answer_flow)
    eval_service = EvaluationService(
        retrieval_metrics=RetrievalMetrics(),
        generation_metrics=GenerationMetrics(embedder=embedder),
        ragas_adapter=RAGASAdapter(answer_runtime.failover_service),
        answer_flow=answer_runtime.answer_flow,
        default_ks=[int(value) for value in raw_config.get("default_ks", [1, 3, 5, 10])],
    )
    runtime = EvaluationRuntime(
        dataset_manager=GoldenDatasetManager(
            base_path=str(Path(__file__).resolve().parents[3] / "eval" / "datasets")
        ),
        eval_service=eval_service,
        regression_runner=RegressionTestRunner(
            eval_service=eval_service,
            baseline_path=str(Path(__file__).resolve().parents[3] / "eval" / "datasets" / "regression"),
            regression_tolerance=float(raw_config.get("regression_tolerance", 0.05)),
            latency_tolerance=float(raw_config.get("latency_tolerance", 0.20)),
        ),
        default_use_ragas=bool(raw_config.get("use_ragas_by_default", False)),
    )
    request.app.state.evaluation_runtime = runtime
    request.app.state.last_eval_request_id = RequestId.generate().value
    return runtime


def _resolve_embedder(answer_flow) -> object | None:
    """Best-effort extraction of the embedder used by the live retrieval stack."""
    orchestrator = getattr(answer_flow.retrieval_service, "orchestrator", None)
    dense_retriever = getattr(orchestrator, "dense_retriever", None)
    if dense_retriever is not None:
        return getattr(dense_retriever, "embedder", None)
    standard_retrieval = getattr(orchestrator, "standard_retrieval", None)
    if standard_retrieval is not None:
        dense_retriever = getattr(standard_retrieval, "dense_retriever", None)
        return getattr(dense_retriever, "embedder", None)
    return None
