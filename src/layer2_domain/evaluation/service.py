"""Evaluation service."""

from __future__ import annotations

from datetime import datetime, timezone

from src.layer0_core.ids.base import QueryId
from src.layer1_contracts.schemas.evaluation import (
    EvalDataset,
    EvalRunResult,
    GenerationMetricsResult,
    RetrievalMetricsResult,
)
from src.layer1_contracts.schemas.query import Query
from src.layer2_domain.evaluation.generation_metrics import GenerationMetrics
from src.layer2_domain.evaluation.ragas_adapter import RAGASAdapter
from src.layer2_domain.evaluation.retrieval_metrics import RetrievalMetrics
from src.layer3_flows.answer_flow.flow import AnswerFlow


class EvaluationService:
    """Run dataset evaluation against the live answer pipeline."""

    def __init__(
        self,
        retrieval_metrics: RetrievalMetrics,
        generation_metrics: GenerationMetrics,
        ragas_adapter: RAGASAdapter,
        answer_flow: AnswerFlow,
        default_ks: list[int] | None = None,
    ) -> None:
        self.retrieval_metrics = retrieval_metrics
        self.generation_metrics = generation_metrics
        self.ragas_adapter = ragas_adapter
        self.answer_flow = answer_flow
        self.default_ks = default_ks or [1, 3, 5, 10]

    async def evaluate_dataset(self, dataset: EvalDataset, use_ragas: bool = False) -> EvalRunResult:
        """Evaluate every item in a dataset and aggregate the results."""
        retrieval_results: list[RetrievalMetricsResult] = []
        generation_results: list[GenerationMetricsResult] = []
        latencies: list[float] = []
        costs: list[float] = []

        for item in dataset.items:
            started = datetime.now(timezone.utc)
            query = Query(id=item.id or QueryId.generate().value, text=item.query)
            answer, trace = await self.answer_flow.execute(query)
            latency_ms = (datetime.now(timezone.utc) - started).total_seconds() * 1000.0
            latencies.append(latency_ms)
            costs.append(self._estimate_cost(trace))

            retrieved = [citation.chunk_id for citation in answer.citations] or list(answer.evidence_item_ids)
            retrieval_metric = self.retrieval_metrics.evaluate(
                retrieved,
                item.expected_chunks,
                ks=self.default_ks,
            )
            evidence = [citation.quoted_text for citation in answer.citations if citation.quoted_text]
            generation_metric = await self.generation_metrics.evaluate(answer, item, evidence)

            if use_ragas:
                retrieval_metric, generation_metric = await self._apply_ragas(
                    item.query,
                    item.expected_answer or "",
                    answer.text,
                    evidence,
                    retrieval_metric,
                    generation_metric,
                )

            retrieval_results.append(retrieval_metric)
            generation_results.append(generation_metric)

        sorted_latencies = sorted(latencies)
        return EvalRunResult(
            run_id=f"eval-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            dataset_id=dataset.id,
            retrieval_metrics=self._aggregate_retrieval(retrieval_results),
            generation_metrics=self._aggregate_generation(generation_results),
            avg_latency_ms=sum(latencies) / float(len(latencies)) if latencies else 0.0,
            p95_latency_ms=self._percentile(sorted_latencies, 0.95),
            p99_latency_ms=self._percentile(sorted_latencies, 0.99),
            total_cost_usd=sum(costs),
        )

    async def _apply_ragas(
        self,
        query: str,
        ground_truth: str,
        answer_text: str,
        evidence: list[str],
        retrieval_metric: RetrievalMetricsResult,
        generation_metric: GenerationMetricsResult,
    ) -> tuple[RetrievalMetricsResult, GenerationMetricsResult]:
        """Blend RAGAS-style metrics into the aggregate outputs."""
        if not evidence:
            return retrieval_metric, generation_metric
        context_precision = await self.ragas_adapter.context_precision(query, evidence, ground_truth)
        context_recall = await self.ragas_adapter.context_recall(evidence, ground_truth)
        ragas_faithfulness = await self.ragas_adapter.faithfulness(answer_text, evidence)
        ragas_relevance = await self.ragas_adapter.answer_relevancy(query, answer_text)

        retrieval_metric = retrieval_metric.model_copy(
            deep=True,
            update={
                "precision_at_k": {
                    **retrieval_metric.precision_at_k,
                    5: (retrieval_metric.precision_at_k.get(5, 0.0) + context_precision) / 2.0,
                },
                "recall_at_k": {
                    **retrieval_metric.recall_at_k,
                    5: (retrieval_metric.recall_at_k.get(5, 0.0) + context_recall) / 2.0,
                },
            },
        )
        generation_metric = generation_metric.model_copy(
            update={
                "faithfulness": (generation_metric.faithfulness + ragas_faithfulness) / 2.0,
                "relevance": (generation_metric.relevance + ragas_relevance) / 2.0,
            }
        )
        return retrieval_metric, generation_metric

    def _aggregate_retrieval(self, results: list[RetrievalMetricsResult]) -> RetrievalMetricsResult:
        """Aggregate retrieval metrics across all dataset items."""
        ks = self.default_ks
        if not results:
            return RetrievalMetricsResult(
                precision_at_k={k: 0.0 for k in ks},
                recall_at_k={k: 0.0 for k in ks},
                mrr=0.0,
                ndcg_at_k={k: 0.0 for k in ks},
                map_score=0.0,
                hit_rate_at_k={k: 0.0 for k in ks},
            )
        count = float(len(results))
        return RetrievalMetricsResult(
            precision_at_k={k: sum(result.precision_at_k.get(k, 0.0) for result in results) / count for k in ks},
            recall_at_k={k: sum(result.recall_at_k.get(k, 0.0) for result in results) / count for k in ks},
            mrr=sum(result.mrr for result in results) / count,
            ndcg_at_k={k: sum(result.ndcg_at_k.get(k, 0.0) for result in results) / count for k in ks},
            map_score=sum(result.map_score for result in results) / count,
            hit_rate_at_k={k: sum(result.hit_rate_at_k.get(k, 0.0) for result in results) / count for k in ks},
        )

    def _aggregate_generation(self, results: list[GenerationMetricsResult]) -> GenerationMetricsResult:
        """Aggregate generation metrics across all dataset items."""
        if not results:
            return GenerationMetricsResult(
                faithfulness=0.0,
                relevance=0.0,
                citation_precision=0.0,
                citation_recall=0.0,
                answer_similarity=0.0,
                abstention_accuracy=0.0,
            )
        count = float(len(results))
        return GenerationMetricsResult(
            faithfulness=sum(result.faithfulness for result in results) / count,
            relevance=sum(result.relevance for result in results) / count,
            citation_precision=sum(result.citation_precision for result in results) / count,
            citation_recall=sum(result.citation_recall for result in results) / count,
            answer_similarity=sum(result.answer_similarity for result in results) / count,
            abstention_accuracy=sum(result.abstention_accuracy for result in results) / count,
        )

    @staticmethod
    def _estimate_cost(trace) -> float:
        """Estimate provider cost from generation trace token counts."""
        costs = {
            "gpt-4o": 5.0,
            "gpt-4o-mini": 0.15,
            "claude-sonnet-4-20250514": 3.0,
        }
        rate = costs.get(trace.model_used, 1.0) / 1_000_000.0
        return (trace.prompt_tokens + trace.completion_tokens) * rate

    @staticmethod
    def _percentile(values: list[float], percentile: float) -> float:
        """Return a stable percentile for a sorted list."""
        if not values:
            return 0.0
        index = min(max(int((len(values) - 1) * percentile), 0), len(values) - 1)
        return values[index]
