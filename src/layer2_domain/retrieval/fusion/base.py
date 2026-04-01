"""Fusion strategy contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.layer1_contracts.schemas.retrieval import RetrievalCandidate


class FusionStrategy(ABC):
    """Abstract strategy for combining candidate lists."""

    @abstractmethod
    def fuse(
        self,
        dense_candidates: list[RetrievalCandidate],
        lexical_candidates: list[RetrievalCandidate],
        top_k: int,
    ) -> list[RetrievalCandidate]:
        """Fuse dense and lexical candidate lists."""
