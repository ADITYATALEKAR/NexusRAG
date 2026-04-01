"""Lexical store interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class LexicalStoreInterface(ABC):
    """Abstract interface for keyword search backends."""

    @abstractmethod
    async def index(self, id: str, content: str, metadata: dict | None = None) -> None:
        """Index a document."""

    @abstractmethod
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter: dict | None = None,
    ) -> list[tuple[str, float]]:
        """Search the lexical index."""

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete a document from the lexical index."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return backend health."""
