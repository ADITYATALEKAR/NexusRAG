"""Candidate deduplication helpers."""

from __future__ import annotations

from src.layer1_contracts.schemas.retrieval import RetrievalCandidate


class CandidateDeduplicator:
    """Remove duplicate candidates while preserving the highest scored copy."""

    def __init__(self, similarity_threshold: float = 0.95) -> None:
        self.similarity_threshold = similarity_threshold

    def deduplicate(self, candidates: list[RetrievalCandidate]) -> list[RetrievalCandidate]:
        """Deduplicate candidates by chunk id."""
        deduped: list[RetrievalCandidate] = []
        seen: set[str] = set()
        for candidate in sorted(candidates, key=lambda item: item.scores.final_score, reverse=True):
            if candidate.chunk_id in seen:
                continue
            seen.add(candidate.chunk_id)
            deduped.append(candidate.model_copy(deep=True))

        for index, candidate in enumerate(deduped):
            candidate.rank = index
        return deduped

    def deduplicate_by_content(self, candidates: list[RetrievalCandidate]) -> list[RetrievalCandidate]:
        """Deduplicate candidates by approximate content overlap."""
        deduped: list[RetrievalCandidate] = []
        for candidate in sorted(candidates, key=lambda item: item.scores.final_score, reverse=True):
            duplicate = False
            for existing in deduped:
                if self._jaccard_similarity(candidate.content, existing.content) >= self.similarity_threshold:
                    duplicate = True
                    break
            if not duplicate:
                deduped.append(candidate.model_copy(deep=True))

        for index, candidate in enumerate(deduped):
            candidate.rank = index
        return deduped

    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        union = words1 | words2
        if not union:
            return 0.0
        return len(words1 & words2) / len(union)
