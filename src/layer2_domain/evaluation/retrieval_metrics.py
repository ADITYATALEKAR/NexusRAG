"""Retrieval evaluation metrics."""

from __future__ import annotations

import math

from src.layer1_contracts.schemas.evaluation import RetrievalMetricsResult


class RetrievalMetrics:
    """Calculate retrieval quality metrics."""

    @staticmethod
    def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
        """Precision@K = relevant in top-k / k."""
        if k <= 0:
            return 0.0
        return len(set(retrieved[:k]) & relevant) / float(k)

    @staticmethod
    def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
        """Recall@K = relevant in top-k / total relevant."""
        if not relevant:
            return 1.0
        return len(set(retrieved[:k]) & relevant) / float(len(relevant))

    @staticmethod
    def mrr(retrieved: list[str], relevant: set[str]) -> float:
        """Mean Reciprocal Rank = inverse rank of first relevant hit."""
        for index, item in enumerate(retrieved, start=1):
            if item in relevant:
                return 1.0 / float(index)
        return 0.0

    @staticmethod
    def ndcg_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
        """Normalized discounted cumulative gain."""

        def dcg(items: list[str], n: int) -> float:
            total = 0.0
            for index, item in enumerate(items[:n]):
                relevance = 1.0 if item in relevant else 0.0
                total += relevance / math.log2(index + 2)
            return total

        score = dcg(retrieved, k)
        ideal = dcg(list(relevant)[:k], k)
        return score / ideal if ideal > 0 else 0.0

    @staticmethod
    def average_precision(retrieved: list[str], relevant: set[str]) -> float:
        """Average precision used in MAP."""
        if not relevant:
            return 1.0
        hits = 0
        total = 0.0
        for index, item in enumerate(retrieved, start=1):
            if item in relevant:
                hits += 1
                total += hits / float(index)
        return total / float(len(relevant))

    @staticmethod
    def hit_rate_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
        """Return 1.0 if any relevant hit exists in top-k, else 0.0."""
        return 1.0 if set(retrieved[:k]) & relevant else 0.0

    def evaluate(
        self,
        retrieved: list[str],
        relevant: list[str],
        ks: list[int] | None = None,
    ) -> RetrievalMetricsResult:
        """Evaluate one retrieved ranking."""
        values = ks or [1, 3, 5, 10]
        relevant_set = set(relevant)
        return RetrievalMetricsResult(
            precision_at_k={k: self.precision_at_k(retrieved, relevant_set, k) for k in values},
            recall_at_k={k: self.recall_at_k(retrieved, relevant_set, k) for k in values},
            mrr=self.mrr(retrieved, relevant_set),
            ndcg_at_k={k: self.ndcg_at_k(retrieved, relevant_set, k) for k in values},
            map_score=self.average_precision(retrieved, relevant_set),
            hit_rate_at_k={k: self.hit_rate_at_k(retrieved, relevant_set, k) for k in values},
        )
