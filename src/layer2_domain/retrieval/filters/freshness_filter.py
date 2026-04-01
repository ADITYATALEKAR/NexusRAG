"""Freshness boosting for retrieval candidates."""

from __future__ import annotations

from datetime import datetime, timezone
import math

from src.layer1_contracts.schemas.retrieval import RetrievalCandidate
from src.layer1_contracts.interfaces.metadata_store import MetadataStoreInterface


class FreshnessBooster:
    """Apply exponential freshness boosts to final scores."""

    def __init__(self, decay_days: int = 30, max_boost: float = 0.2) -> None:
        self.decay_days = decay_days
        self.max_boost = max_boost

    def apply(
        self,
        candidates: list[RetrievalCandidate],
        metadata_store: MetadataStoreInterface,
    ) -> list[RetrievalCandidate]:
        """Boost candidate scores based on recency and return a re-ranked list."""
        now = datetime.now(timezone.utc)
        boosted: list[RetrievalCandidate] = []

        for candidate in candidates:
            boosted_candidate = candidate.model_copy(deep=True)
            chunk_meta = metadata_store.get_chunk_sync(candidate.chunk_id)
            if chunk_meta and chunk_meta.get("created_at"):
                created_at = datetime.fromisoformat(chunk_meta["created_at"])
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                age_days = max((now - created_at).days, 0)
                freshness_boost = self.max_boost * math.exp(-age_days / self.decay_days)
                boosted_candidate.scores.final_score += freshness_boost
            boosted.append(boosted_candidate)

        boosted.sort(key=lambda item: item.scores.final_score, reverse=True)
        for index, candidate in enumerate(boosted):
            candidate.rank = index
        return boosted
