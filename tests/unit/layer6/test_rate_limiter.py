"""Unit tests for Phase 8 rate limiting."""

from __future__ import annotations

import pytest

from src.layer6_security.rate_limiting.backends import MemoryBackend
from src.layer6_security.rate_limiting.limiter import RateLimiter


@pytest.mark.asyncio
async def test_memory_backend_increments_and_returns_counts() -> None:
    """The in-memory backend should increment and read counters."""
    backend = MemoryBackend()
    assert await backend.get("example") is None
    assert await backend.incr("example", ttl=60) == 1
    assert await backend.incr("example", ttl=60) == 2
    assert await backend.get("example") == 2


@pytest.mark.asyncio
async def test_rate_limiter_blocks_after_threshold_and_prefers_api_key() -> None:
    """The limiter should prefer API-key identity and block after the threshold."""
    limiter = RateLimiter(MemoryBackend(), requests_per_minute=1, requests_per_hour=10)

    key = limiter.get_key(ip="127.0.0.1", api_key="secret-key")
    assert key.startswith("ratelimit:key:")

    allowed, info = await limiter.is_allowed(key)
    assert allowed is True
    assert info["limit_minute"] == 1

    blocked, blocked_info = await limiter.is_allowed(key)
    assert blocked is False
    assert blocked_info["remaining_minute"] == 0


@pytest.mark.asyncio
async def test_rate_limiter_describe_reports_headers_without_consuming_quota() -> None:
    """Describe should expose header metadata without incrementing counters."""
    limiter = RateLimiter(MemoryBackend(), requests_per_minute=2, requests_per_hour=10)
    key = limiter.get_key(ip="127.0.0.1")

    initial = await limiter.describe(key)
    assert initial["limit_minute"] == 2
    assert initial["remaining_minute"] == 2

    allowed, _ = await limiter.is_allowed(key)
    assert allowed is True

    described = await limiter.describe(key)
    assert described["remaining_minute"] == 1
