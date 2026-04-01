"""Reciprocal rank fusion."""

from __future__ import annotations

from src.layer1_contracts.schemas.retrieval import RetrievalCandidate, RetrievalSource
from src.layer2_domain.retrieval.fusion.base import FusionStrategy


class ReciprocalRankFusion(FusionStrategy):
    """Fuse ranked lists with reciprocal rank fusion."""

    def __init__(self, k: int = 60) -> None:
        self.k = k

    def fuse(
        self,
        dense_candidates: list[RetrievalCandidate],
        lexical_candidates: list[RetrievalCandidate],
        top_k: int,
    ) -> list[RetrievalCandidate]:
        """Fuse dense and lexical rankings using reciprocal rank fusion."""
        candidate_map: dict[str, RetrievalCandidate] = {}
        rrf_scores: dict[str, float] = {}

        for candidate in dense_candidates:
            chunk_id = candidate.chunk_id
            score = 1.0 / (self.k + candidate.rank + 1)
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + score
            if chunk_id not in candidate_map:
                candidate_map[chunk_id] = candidate.model_copy(deep=True)
            candidate_map[chunk_id].scores.dense_score = candidate.scores.dense_score

        for candidate in lexical_candidates:
            chunk_id = candidate.chunk_id
            score = 1.0 / (self.k + candidate.rank + 1)
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + score
            if chunk_id not in candidate_map:
                candidate_map[chunk_id] = candidate.model_copy(deep=True)
            candidate_map[chunk_id].scores.lexical_score = candidate.scores.lexical_score

        fused: list[RetrievalCandidate] = []
        sorted_ids = sorted(rrf_scores, key=rrf_scores.get, reverse=True)[:top_k]
        for index, chunk_id in enumerate(sorted_ids):
            candidate = candidate_map[chunk_id]
            candidate.scores.fusion_score = rrf_scores[chunk_id]
            candidate.scores.final_score = rrf_scores[chunk_id]
            candidate.source = RetrievalSource.HYBRID
            candidate.rank = index
            fused.append(candidate)
        return fused
