"""Cache interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CacheInterface(ABC):
    """Abstract interface for caching."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Get a value from cache."""

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Set a value in cache."""

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a cache key."""

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Return whether a key exists."""

    @abstractmethod
    async def clear(self) -> None:
        """Clear the cache."""
