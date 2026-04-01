"""Trust-score filtering."""

from __future__ import annotations

from src.layer1_contracts.schemas.retrieval import RetrievalCandidate
from src.layer1_contracts.interfaces.metadata_store import MetadataStoreInterface


class TrustFilter:
    """Filter candidates by document trust score."""

    def __init__(self, metadata_store: MetadataStoreInterface | None = None) -> None:
        self.metadata_store = metadata_store

    def apply(
        self,
        candidates: list[RetrievalCandidate],
        min_trust: float,
        trust_scores: dict[str, float] | None = None,
    ) -> list[RetrievalCandidate]:
        """Filter candidates whose trust score is below the configured threshold."""
        filtered: list[RetrievalCandidate] = []
        for candidate in candidates:
            trust = self._lookup_trust(candidate, trust_scores)
            if trust >= min_trust:
                filtered.append(candidate.model_copy(deep=True))

        for index, candidate in enumerate(filtered):
            candidate.rank = index
        return filtered

    def _lookup_trust(
        self,
        candidate: RetrievalCandidate,
        trust_scores: dict[str, float] | None,
    ) -> float:
        if trust_scores and candidate.document_id in trust_scores:
            return trust_scores[candidate.document_id]
        if self.metadata_store is not None:
            metadata = self.metadata_store.get_chunk_sync(candidate.chunk_id) or {}
            if metadata.get("trust_score") is not None:
                return float(metadata["trust_score"])
        return 1.0
