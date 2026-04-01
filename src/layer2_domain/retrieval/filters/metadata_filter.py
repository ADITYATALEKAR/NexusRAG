"""Metadata-driven candidate filtering."""

from __future__ import annotations

from datetime import datetime

from src.layer1_contracts.schemas.retrieval import RetrievalCandidate
from src.layer1_contracts.schemas.retrieval_config import FilterConfig
from src.layer1_contracts.interfaces.metadata_store import MetadataStoreInterface


class MetadataFilter:
    """Filter retrieval candidates by stored metadata."""

    def __init__(self, metadata_store: MetadataStoreInterface | None = None) -> None:
        self.metadata_store = metadata_store

    def apply(
        self,
        candidates: list[RetrievalCandidate],
        config: FilterConfig,
    ) -> list[RetrievalCandidate]:
        """Apply metadata filters and re-rank the retained candidates."""
        filtered: list[RetrievalCandidate] = []
        for candidate in candidates:
            if self._matches(candidate, config):
                filtered.append(candidate.model_copy(deep=True))

        for index, candidate in enumerate(filtered):
            candidate.rank = index
        return filtered

    def _matches(self, candidate: RetrievalCandidate, config: FilterConfig) -> bool:
        metadata = self._lookup(candidate.chunk_id)
        if config.document_ids and candidate.document_id not in config.document_ids:
            return False
        if config.exclude_chunk_ids and candidate.chunk_id in config.exclude_chunk_ids:
            return False
        if config.document_types and metadata.get("document_type") not in config.document_types:
            return False
        if config.tags:
            candidate_tags = set(metadata.get("tags", []))
            if not candidate_tags.intersection(config.tags):
                return False
        if config.date_from or config.date_to:
            created_at_raw = metadata.get("created_at")
            if created_at_raw is None:
                return False
            created_at = datetime.fromisoformat(created_at_raw)
            if config.date_from and created_at < datetime.fromisoformat(config.date_from):
                return False
            if config.date_to and created_at > datetime.fromisoformat(config.date_to):
                return False
        return True

    def _lookup(self, chunk_id: str) -> dict:
        if self.metadata_store is None:
            return {}
        return self.metadata_store.get_chunk_sync(chunk_id) or {}
