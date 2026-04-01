"""Reranker interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class RerankerInterface(ABC):
    """Abstract interface for reranking providers."""

    @property
    @abstractmethod
    def model(self) -> str:
        """Return the model name."""

    @abstractmethod
    async def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int | None = None,
    ) -> list[tuple[int, float]]:
        """Return ranked document indices and scores."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return provider health."""
