"""Request rate limiting logic."""

from __future__ import annotations

from datetime import datetime
import hashlib

from src.layer6_security.rate_limiting.backends import RateLimitBackend


class RateLimiter:
    """Check per-minute and per-hour rate limits for API callers."""

    def __init__(
        self,
        backend: RateLimitBackend,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10,
    ) -> None:
        self.backend = backend
        self.rpm = requests_per_minute
        self.rph = requests_per_hour
        self.burst = burst_size

    async def is_allowed(self, key: str) -> tuple[bool, dict[str, int]]:
        """Return whether a request should be allowed plus rate limit metadata."""
        now = datetime.utcnow()
        minute_key, hour_key = self._window_keys(key, now)
        minute_count, hour_count = await self._counts_for_window(minute_key, hour_key)
        info = self._build_info(now, minute_count, hour_count)
        if minute_count >= self.rpm or hour_count >= self.rph:
            return False, info

        updated_minute_count = await self.backend.incr(minute_key, ttl=60)
        updated_hour_count = await self.backend.incr(hour_key, ttl=3600)
        info["remaining_minute"] = max(0, self.rpm - updated_minute_count)
        info["remaining_hour"] = max(0, self.rph - updated_hour_count)
        return True, info

    async def describe(self, key: str) -> dict[str, int]:
        """Return rate-limit metadata without consuming quota."""
        now = datetime.utcnow()
        minute_key, hour_key = self._window_keys(key, now)
        minute_count, hour_count = await self._counts_for_window(minute_key, hour_key)
        return self._build_info(now, minute_count, hour_count)

    def get_key(self, ip: str | None = None, api_key: str | None = None) -> str:
        """Generate a stable rate limit key from either API key or client IP."""
        if api_key:
            digest = hashlib.sha256(api_key.encode("utf-8")).hexdigest()[:16]
            return f"ratelimit:key:{digest}"
        return f"ratelimit:ip:{ip or 'unknown'}"

    def _window_keys(self, key: str, now: datetime) -> tuple[str, str]:
        """Build minute and hour bucket keys for the current request window."""
        minute_key = f"{key}:m:{now.strftime('%Y%m%d%H%M')}"
        hour_key = f"{key}:h:{now.strftime('%Y%m%d%H')}"
        return minute_key, hour_key

    async def _counts_for_window(self, minute_key: str, hour_key: str) -> tuple[int, int]:
        """Fetch the current counts for the active minute and hour buckets."""
        minute_count = await self.backend.get(minute_key) or 0
        hour_count = await self.backend.get(hour_key) or 0
        return minute_count, hour_count

    def _build_info(self, now: datetime, minute_count: int, hour_count: int) -> dict[str, int]:
        """Build standard rate-limit metadata for headers and responses."""
        return {
            "limit_minute": self.rpm,
            "remaining_minute": max(0, self.rpm - minute_count),
            "limit_hour": self.rph,
            "remaining_hour": max(0, self.rph - hour_count),
            "reset_minute": max(1, 60 - now.second),
            "reset_hour": max(1, 3600 - (now.minute * 60 + now.second)),
        }
