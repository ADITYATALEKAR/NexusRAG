"""Rate limit backend implementations."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Protocol


class RateLimitBackend(Protocol):
    """Minimal backend contract used by the rate limiter."""

    async def get(self, key: str) -> int | None:
        """Return the current counter for a key."""

    async def incr(self, key: str, ttl: int = 60) -> int:
        """Increment a key with the provided time-to-live."""

    async def close(self) -> None:
        """Release backend resources."""


class MemoryBackend:
    """In-memory rate limit backend for development and tests."""

    def __init__(self) -> None:
        self._data: dict[str, tuple[int, datetime]] = {}

    async def get(self, key: str) -> int | None:
        """Return the current count if the key has not expired."""
        if key in self._data:
            count, expires_at = self._data[key]
            if datetime.utcnow() < expires_at:
                return count
            del self._data[key]
        return None

    async def incr(self, key: str, ttl: int = 60) -> int:
        """Increment the counter and extend or establish its expiry."""
        now = datetime.utcnow()
        if key in self._data:
            count, expires_at = self._data[key]
            if now < expires_at:
                new_count = count + 1
                self._data[key] = (new_count, expires_at)
                return new_count
        self._data[key] = (1, now + timedelta(seconds=ttl))
        return 1

    async def close(self) -> None:
        """Release memory-held counters."""
        self._data.clear()


class RedisBackend:
    """Redis-backed rate limit backend for production use."""

    def __init__(self, redis_url: str) -> None:
        import redis.asyncio as redis

        self._redis = redis.from_url(redis_url)

    async def get(self, key: str) -> int | None:
        """Return the current counter from Redis."""
        value = await self._redis.get(key)
        return int(value) if value is not None else None

    async def incr(self, key: str, ttl: int = 60) -> int:
        """Increment the Redis key and refresh its expiry."""
        pipeline = self._redis.pipeline()
        pipeline.incr(key)
        pipeline.expire(key, ttl)
        result = await pipeline.execute()
        return int(result[0])

    async def close(self) -> None:
        """Close the Redis connection pool."""
        await self._redis.aclose()
