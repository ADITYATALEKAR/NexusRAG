"""Embedder interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class EmbedderInterface(ABC):
    """Abstract interface for embedding providers."""

    @property
    @abstractmethod
    def model(self) -> str:
        """Return the model name."""

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Return vector dimensions."""

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""

    @abstractmethod
    async def embed_query(self, query: str) -> list[float]:
        """Generate an embedding for a single query."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return provider health."""
