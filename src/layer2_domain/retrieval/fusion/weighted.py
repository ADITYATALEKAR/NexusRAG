"""Weighted score fusion."""

from __future__ import annotations

from src.layer1_contracts.schemas.retrieval import RetrievalCandidate, RetrievalSource
from src.layer2_domain.reranking.score_normalizer import ScoreNormalizer
from src.layer2_domain.retrieval.fusion.base import FusionStrategy


class WeightedScoreFusion(FusionStrategy):
    """Fuse candidates with weighted normalized scores."""

    def __init__(self, dense_weight: float = 0.5, lexical_weight: float = 0.5) -> None:
        self.dense_weight = dense_weight
        self.lexical_weight = lexical_weight

    def fuse(
        self,
        dense_candidates: list[RetrievalCandidate],
        lexical_candidates: list[RetrievalCandidate],
        top_k: int,
    ) -> list[RetrievalCandidate]:
        """Fuse lists with weighted normalized scores."""
        dense_normalized = ScoreNormalizer.min_max_normalize(
            [candidate.scores.dense_score or 0.0 for candidate in dense_candidates]
        )
        lexical_normalized = ScoreNormalizer.min_max_normalize(
            [candidate.scores.lexical_score or 0.0 for candidate in lexical_candidates]
        )

        candidate_map: dict[str, RetrievalCandidate] = {}
        combined_scores: dict[str, float] = {}

        for candidate, normalized_score in zip(dense_candidates, dense_normalized):
            chunk_id = candidate.chunk_id
            combined_scores[chunk_id] = self.dense_weight * normalized_score
            candidate_map[chunk_id] = candidate.model_copy(deep=True)
            candidate_map[chunk_id].scores.dense_score = candidate.scores.dense_score

        for candidate, normalized_score in zip(lexical_candidates, lexical_normalized):
            chunk_id = candidate.chunk_id
            if chunk_id not in candidate_map:
                candidate_map[chunk_id] = candidate.model_copy(deep=True)
            candidate_map[chunk_id].scores.lexical_score = candidate.scores.lexical_score
            combined_scores[chunk_id] = combined_scores.get(chunk_id, 0.0) + (
                self.lexical_weight * normalized_score
            )

        fused: list[RetrievalCandidate] = []
        sorted_ids = sorted(combined_scores, key=combined_scores.get, reverse=True)[:top_k]
        for index, chunk_id in enumerate(sorted_ids):
            candidate = candidate_map[chunk_id]
            candidate.scores.fusion_score = combined_scores[chunk_id]
            candidate.scores.final_score = combined_scores[chunk_id]
            candidate.source = RetrievalSource.HYBRID
            candidate.rank = index
            fused.append(candidate)
        return fused
