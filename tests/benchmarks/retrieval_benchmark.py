"""Benchmark harness for retrieval quality and latency."""

from __future__ import annotations

from src.layer0_core.ids.base import QueryId
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.retrieval_config import RetrievalConfig
from src.layer2_domain.retrieval.service import RetrievalService


class RetrievalBenchmark:
    """Benchmark retrieval quality and latency."""

    def __init__(self, retrieval_service: RetrievalService, golden_set: list[dict]):
        """Store the retrieval service and benchmark golden set."""
        self.service = retrieval_service
        self.golden_set = golden_set

    async def run(self, config: RetrievalConfig) -> dict:
        """Run the benchmark and return aggregated metrics."""
        results = {
            "precision_at_k": [],
            "recall_at_k": [],
            "mrr": [],
            "latency_ms": [],
        }

        for item in self.golden_set:
            query = Query(id=QueryId.generate().value, text=item["query"])
            result = await self.service.retrieve(query, config)

            retrieved_ids = [candidate.chunk_id for candidate in result.candidates]
            relevant_ids = set(item["relevant_chunk_ids"])
            hits = len(set(retrieved_ids) & relevant_ids)
            precision = hits / len(retrieved_ids) if retrieved_ids else 0.0
            recall = hits / len(relevant_ids) if relevant_ids else 0.0
            reciprocal_rank = 0.0
            for rank, chunk_id in enumerate(retrieved_ids, 1):
                if chunk_id in relevant_ids:
                    reciprocal_rank = 1.0 / rank
                    break

            results["precision_at_k"].append(precision)
            results["recall_at_k"].append(recall)
            results["mrr"].append(reciprocal_rank)
            results["latency_ms"].append(result.total_latency_ms)

        latency_values = sorted(results["latency_ms"])
        p99_index = min(len(latency_values) - 1, max(0, int(len(latency_values) * 0.99)))
        return {
            "avg_precision": sum(results["precision_at_k"]) / len(results["precision_at_k"]),
            "avg_recall": sum(results["recall_at_k"]) / len(results["recall_at_k"]),
            "avg_mrr": sum(results["mrr"]) / len(results["mrr"]),
            "avg_latency_ms": sum(results["latency_ms"]) / len(results["latency_ms"]),
            "p99_latency_ms": latency_values[p99_index],
        }
