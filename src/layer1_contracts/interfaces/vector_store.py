"""Vector store interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class VectorStoreInterface(ABC):
    """Abstract backend-agnostic vector store interface."""

    @abstractmethod
    async def insert(
        self,
        ids: list[str],
        vectors: list[list[float]],
        metadata: list[dict] | None = None,
    ) -> int:
        """Insert vectors and return the count inserted."""

    @abstractmethod
    async def upsert(
        self,
        ids: list[str],
        vectors: list[list[float]],
        metadata: list[dict] | None = None,
    ) -> int:
        """Insert or update vectors."""

    @abstractmethod
    async def delete(self, ids: list[str]) -> int:
        """Delete vectors by ID and return the count removed."""

    @abstractmethod
    async def search(
        self,
        query_vector: list[float],
        top_k: int = 10,
        filter: dict | None = None,
    ) -> list[tuple[str, float, dict | None]]:
        """Search for similar vectors."""

    @abstractmethod
    async def fetch(self, ids: list[str]) -> list[tuple[str, list[float], dict | None]]:
        """Fetch vectors by ID."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return backend health."""

    @abstractmethod
    async def collection_exists(self, name: str) -> bool:
        """Return whether a collection exists."""

    @abstractmethod
    async def count(self) -> int:
        """Return the total vector count."""
