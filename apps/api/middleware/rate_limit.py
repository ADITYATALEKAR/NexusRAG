"""HTTP rate limiting middleware."""

from __future__ import annotations

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.layer6_security.rate_limiting.limiter import RateLimiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Apply request throttling based on IP address or API key."""

    def __init__(
        self,
        app,
        limiter: RateLimiter | None = None,
        enabled: bool = False,
        exclude_paths: list[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.limiter = limiter
        self.enabled = enabled
        self.exclude = set(
            exclude_paths
            or [
                "/health",
                "/health/",
                "/health/liveness",
                "/health/readiness",
            ]
        )

    async def dispatch(self, request: Request, call_next):
        """Block or annotate requests according to the configured limits."""
        limiter = self.limiter or getattr(request.app.state, "rate_limiter", None)
        enabled = self.enabled or getattr(request.app.state, "rate_limit_enabled", False)
        if not enabled or limiter is None:
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        client_ip = request.client.host if request.client else "unknown"
        key = limiter.get_key(ip=client_ip, api_key=api_key)

        if request.url.path in self.exclude:
            response = await call_next(request)
            info = await limiter.describe(key)
            self._apply_headers(response, info)
            return response

        allowed, info = await limiter.is_allowed(key)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "retry_after": info["reset_minute"]},
                headers={
                    "X-RateLimit-Limit": str(info["limit_minute"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(info["reset_minute"]),
                    "Retry-After": str(info["reset_minute"]),
                },
            )

        response = await call_next(request)
        self._apply_headers(response, info)
        return response

    @staticmethod
    def _apply_headers(response, info: dict[str, int]) -> None:
        """Attach standard rate-limit headers to a response."""
        response.headers["X-RateLimit-Limit"] = str(info["limit_minute"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining_minute"])
        response.headers["X-RateLimit-Reset"] = str(info["reset_minute"])
