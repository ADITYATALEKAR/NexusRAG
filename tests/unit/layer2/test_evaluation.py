"""Unit tests for Phase 7 evaluation services."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.layer1_contracts.schemas.answer import Answer, AnswerMetadata, AnswerStatus, Citation
from src.layer1_contracts.schemas.evaluation import (
    EvalDataset,
    EvalDatasetItem,
    EvalRunResult,
    GenerationMetricsResult,
    RetrievalMetricsResult,
)
from src.layer1_contracts.schemas.generation import GenerationTrace
from src.layer1_contracts.schemas.health import HealthStatus, ProviderHealth
from src.layer1_contracts.schemas.llm import LLMConfig, LLMResponse, LLMUsage, Message, MessageRole
from src.layer2_domain.evaluation.dataset_manager import GoldenDatasetManager
from src.layer2_domain.evaluation.generation_metrics import GenerationMetrics
from src.layer2_domain.evaluation.ragas_adapter import RAGASAdapter
from src.layer2_domain.evaluation.regression import RegressionTestRunner
from src.layer2_domain.evaluation.retrieval_metrics import RetrievalMetrics
from src.layer2_domain.evaluation.service import EvaluationService


class StubAnswerFlow:
    """Answer flow stub for evaluation tests."""

    async def execute(self, query, *_args, **_kwargs):
        answer = Answer(
            id=f"ans-{query.id}",
            query_id=query.id,
            text="Hybrid retrieval combines dense vectors and lexical BM25 search.",
            status=AnswerStatus.SUCCESS,
            citations=[
                Citation(
                    citation_key="[1]",
                    chunk_id="chunk-1",
                    document_id="doc-1",
                    quoted_text="Hybrid retrieval combines dense vectors and lexical BM25 search.",
                )
            ],
            evidence_bundle_id=query.id,
            evidence_item_ids=["chunk-1"],
            metadata=AnswerMetadata(
                model_used="gpt-4o-mini",
                provider_used="mock-primary",
                prompt_tokens=100,
                completion_tokens=20,
            ),
        )
        trace = GenerationTrace(
            request_id=query.id,
            query_text=query.text,
            evidence_items=["chunk-1"],
            prompt_tokens=100,
            completion_tokens=20,
            provider_used="mock-primary",
            model_used="gpt-4o-mini",
            fallback_occurred=False,
            fallback_chain=[],
            latency_ms=15,
        )
        return answer, trace


class StubFailoverService:
    """Failover stub for RAGAS adapter tests."""

    def __init__(self, content: str = "1,1,0") -> None:
        self.content = content
        self.requests = []

    async def execute(self, request):
        self.requests.append(request)
        return LLMResponse(
            request_id=request.id,
            content=self.content,
            provider="mock-ragas",
            model=request.config.model,
            usage=LLMUsage(prompt_tokens=5, completion_tokens=3, total_tokens=8),
            latency_ms=10,
            finish_reason="stop",
        )


class StubRAGASAdapter:
    """RAGAS adapter stub that records invocation counts."""

    def __init__(self) -> None:
        self.calls = 0

    async def context_precision(self, *_args, **_kwargs) -> float:
        self.calls += 1
        return 0.8

    async def context_recall(self, *_args, **_kwargs) -> float:
        self.calls += 1
        return 0.7

    async def faithfulness(self, *_args, **_kwargs) -> float:
        self.calls += 1
        return 0.9

    async def answer_relevancy(self, *_args, **_kwargs) -> float:
        self.calls += 1
        return 0.85


class StubEvaluationService:
    """Evaluation service stub for regression runner tests."""

    def __init__(self, result: EvalRunResult) -> None:
        self.result = result

    async def evaluate_dataset(self, dataset, use_ragas: bool = False):  # noqa: ARG002
        return self.result


def _dataset() -> EvalDataset:
    return EvalDataset(
        id="golden-1",
        name="Golden",
        version="1.0",
        items=[
            EvalDatasetItem(
                id="item-1",
                query="What is hybrid retrieval?",
                expected_chunks=["chunk-1"],
                expected_answer="Hybrid retrieval combines dense vectors and lexical BM25 search.",
                expected_citations=["chunk-1"],
            )
        ],
    )


def test_retrieval_metrics_calculate_expected_values() -> None:
    """Retrieval metrics should compute precision, recall, MRR, and MAP correctly."""
    result = RetrievalMetrics().evaluate(["chunk-1", "chunk-2"], ["chunk-1", "chunk-3"], ks=[1, 2])

    assert result.precision_at_k[1] == 1.0
    assert result.recall_at_k[2] == 0.5
    assert result.mrr == 1.0
    assert result.map_score == 0.5
    assert result.hit_rate_at_k[2] == 1.0


@pytest.mark.asyncio
async def test_generation_metrics_calculate_grounding_and_similarity() -> None:
    """Generation metrics should score grounded cited answers correctly."""
    item = _dataset().items[0]
    answer = Answer(
        id="ans-1",
        query_id="item-1",
        text="Hybrid retrieval combines dense vectors and lexical BM25 search.",
        status=AnswerStatus.SUCCESS,
        citations=[Citation(citation_key="[1]", chunk_id="chunk-1", document_id="doc-1")],
        evidence_bundle_id="item-1",
        evidence_item_ids=["chunk-1"],
        metadata=AnswerMetadata(model_used="gpt-4o-mini", provider_used="mock-primary"),
    )

    result = await GenerationMetrics().evaluate(
        answer,
        item,
        ["Hybrid retrieval combines dense vectors and lexical BM25 search."],
    )

    assert result.faithfulness == 1.0
    assert result.citation_precision == 1.0
    assert result.citation_recall == 1.0
    assert result.answer_similarity == 1.0


@pytest.mark.asyncio
async def test_ragas_adapter_calls_llm_runtime() -> None:
    """RAGAS adapter should call the shared LLM runtime for evaluation prompts."""
    service = StubFailoverService(content="0.75")
    adapter = RAGASAdapter(service)

    value = await adapter.answer_relevancy("What is hybrid retrieval?", "It combines dense and lexical search.")

    assert value == 0.75
    assert len(service.requests) == 1
    assert service.requests[0].messages[0].role == MessageRole.USER


def test_dataset_manager_saves_and_loads_dataset(tmp_path) -> None:
    """Golden datasets should round-trip through the dataset manager."""
    manager = GoldenDatasetManager(base_path=str(tmp_path))
    dataset = _dataset()

    path = manager.save(dataset)
    loaded = manager.load(dataset.id)

    assert path.exists()
    assert loaded.id == dataset.id
    assert manager.list_datasets() == [dataset.id]


@pytest.mark.asyncio
async def test_evaluation_service_aggregates_and_uses_ragas() -> None:
    """Evaluation service should aggregate metrics and call RAGAS when enabled."""
    ragas = StubRAGASAdapter()
    service = EvaluationService(
        retrieval_metrics=RetrievalMetrics(),
        generation_metrics=GenerationMetrics(),
        ragas_adapter=ragas,
        answer_flow=StubAnswerFlow(),
    )

    result = await service.evaluate_dataset(_dataset(), use_ragas=True)

    assert result.dataset_id == "golden-1"
    assert result.retrieval_metrics.recall_at_k[5] >= 0.5
    assert result.generation_metrics.faithfulness > 0.9
    assert result.total_cost_usd > 0.0
    assert ragas.calls == 4


@pytest.mark.asyncio
async def test_regression_runner_detects_degradation(tmp_path) -> None:
    """Regression runner should flag degraded recall and latency."""
    baseline = EvalRunResult(
        run_id="baseline",
        dataset_id="golden-1",
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
    current = baseline.model_copy(
        update={
            "run_id": "current",
            "retrieval_metrics": baseline.retrieval_metrics.model_copy(
                update={"recall_at_k": {1: 0.8, 3: 0.8, 5: 0.8, 10: 0.8}}
            ),
            "generation_metrics": baseline.generation_metrics.model_copy(update={"faithfulness": 0.8}),
            "p95_latency_ms": 20.0,
        }
    )
    runner = RegressionTestRunner(
        eval_service=StubEvaluationService(current),
        baseline_path=str(tmp_path),
    )
    runner.save_baseline(baseline, "baseline-1")

    result = await runner.run(_dataset(), "baseline-1")

    assert result.passed is False
    assert any("recall@5" in item for item in result.regressions)
    assert any("faithfulness" in item for item in result.regressions)
    assert any("p95_latency" in item for item in result.regressions)
