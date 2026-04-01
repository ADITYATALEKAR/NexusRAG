"""Evidence selection strategies."""

from __future__ import annotations

from src.layer1_contracts.schemas.evidence import EvidenceConfig, EvidenceItem, EvidenceSelectionStrategy
from src.layer1_contracts.schemas.retrieval import RetrievalCandidate


class EvidenceSelector:
    """Select best evidence items from retrieval candidates."""

    def select(
        self,
        candidates: list[RetrievalCandidate],
        config: EvidenceConfig,
    ) -> list[EvidenceItem]:
        """Select evidence items according to the configured strategy."""
        if config.selection_strategy == EvidenceSelectionStrategy.MMR:
            return self._select_mmr(candidates, config)
        if config.selection_strategy == EvidenceSelectionStrategy.DIVERSITY:
            return self._select_diverse(candidates, config)
        return self._select_top_k(candidates, config)

    def _select_top_k(
        self,
        candidates: list[RetrievalCandidate],
        config: EvidenceConfig,
    ) -> list[EvidenceItem]:
        filtered = [
            candidate
            for candidate in candidates
            if self._normalized_relevance(candidate.scores.final_score) >= config.min_relevance_score
        ]
        selected = filtered[: config.max_evidence_items]
        return [self._candidate_to_evidence(candidate, index) for index, candidate in enumerate(selected)]

    def _select_mmr(
        self,
        candidates: list[RetrievalCandidate],
        config: EvidenceConfig,
        lambda_param: float = 0.5,
    ) -> list[EvidenceItem]:
        """Select diverse evidence with maximal marginal relevance."""
        remaining = [
            candidate
            for candidate in candidates
            if self._normalized_relevance(candidate.scores.final_score) >= config.min_relevance_score
        ]
        if not remaining:
            return []

        selected: list[RetrievalCandidate] = [remaining.pop(0)]
        while len(selected) < config.max_evidence_items and remaining:
            best_index = -1
            best_score = float("-inf")
            for index, candidate in enumerate(remaining):
                relevance = self._normalized_relevance(candidate.scores.final_score)
                max_similarity = max(
                    self._content_similarity(candidate.content, existing.content) for existing in selected
                )
                score = lambda_param * relevance - (1.0 - lambda_param) * max_similarity
                if score > best_score:
                    best_score = score
                    best_index = index
            if best_index >= 0:
                selected.append(remaining.pop(best_index))
            else:
                break

        return [self._candidate_to_evidence(candidate, index) for index, candidate in enumerate(selected)]

    def _select_diverse(
        self,
        candidates: list[RetrievalCandidate],
        config: EvidenceConfig,
    ) -> list[EvidenceItem]:
        """Prefer evidence from distinct documents before allowing duplicates."""
        selected: list[RetrievalCandidate] = []
        seen_documents: set[str] = set()
        for candidate in candidates:
            if len(selected) >= config.max_evidence_items:
                break
            if self._normalized_relevance(candidate.scores.final_score) < config.min_relevance_score:
                continue
            if candidate.document_id not in seen_documents:
                selected.append(candidate)
                seen_documents.add(candidate.document_id)
            elif len(seen_documents) >= 3:
                selected.append(candidate)

        return [self._candidate_to_evidence(candidate, index) for index, candidate in enumerate(selected)]

    def _candidate_to_evidence(self, candidate: RetrievalCandidate, index: int) -> EvidenceItem:
        relevance = self._normalized_relevance(candidate.scores.final_score)
        return EvidenceItem(
            chunk_id=candidate.chunk_id,
            document_id=candidate.document_id,
            content=candidate.content,
            citation_key=f"[{index + 1}]",
            document_title=candidate.document_title,
            section_title=candidate.section_title,
            page_numbers=list(candidate.page_numbers),
            relevance_score=relevance,
        )

    def _normalized_relevance(self, value: float) -> float:
        """Normalize retrieval scores into the evidence schema's 0-1 range."""
        if value <= 0:
            return 0.0
        if value >= 1.0:
            return 1.0
        return float(value)

    def _content_similarity(self, text1: str, text2: str) -> float:
        """Compute simple Jaccard similarity for diversity selection."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        union = words1 | words2
        if not union:
            return 0.0
        return len(words1 & words2) / len(union)
