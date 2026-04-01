"""Reranking service."""

from __future__ import annotations

import time

from src.layer1_contracts.interfaces.reranker import RerankerInterface
from src.layer1_contracts.schemas.retrieval import RetrievalCandidate, RetrievalSource


class RerankingService:
    """Apply cross-encoder style reranking to retrieval candidates."""

    def __init__(self, reranker: RerankerInterface) -> None:
        self.reranker = reranker

    async def rerank(
        self,
        query: str,
        candidates: list[RetrievalCandidate],
        top_k: int,
    ) -> tuple[list[RetrievalCandidate], int]:
        """Rerank candidates and return a new ranked list plus latency."""
        start = time.perf_counter()
        if not candidates:
            return [], 0

        documents = [candidate.content for candidate in candidates]
        ranked_indices = await self.reranker.rerank(query, documents, top_k=top_k)

        reranked: list[RetrievalCandidate] = []
        for new_rank, (original_index, rerank_score) in enumerate(ranked_indices):
            candidate = candidates[original_index].model_copy(deep=True)
            candidate.scores.rerank_score = rerank_score
            candidate.scores.final_score = rerank_score
            candidate.source = RetrievalSource.RERANKED
            candidate.rank = new_rank
            reranked.append(candidate)

        latency_ms = int((time.perf_counter() - start) * 1000)
        return reranked, latency_ms
