"""API key authentication middleware."""

from __future__ import annotations

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.layer6_security.auth.api_key import APIKeyAuth


class AuthMiddleware(BaseHTTPMiddleware):
    """Protect API routes using header-based API key auth."""

    def __init__(
        self,
        app,
        auth: APIKeyAuth | None = None,
        enabled: bool = False,
        exclude_paths: list[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.auth = auth
        self.enabled = enabled
        self.exclude_paths = set(
            exclude_paths
            or [
                "/health",
                "/health/",
                "/health/liveness",
                "/health/readiness",
                "/openapi.json",
                "/docs",
                "/docs/oauth2-redirect",
                "/redoc",
            ]
        )

    async def dispatch(self, request: Request, call_next):
        """Reject requests with missing or invalid API keys when enabled."""
        auth = self.auth or getattr(request.app.state, "api_key_auth", None)
        runtime_config = getattr(request.app.state, "runtime_config", None)
        enabled = self.enabled or bool(
            runtime_config and getattr(runtime_config.security, "api_key_required", False)
        )
        if not enabled or request.method == "OPTIONS" or request.url.path in self.exclude_paths:
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"detail": "API key required"},
                headers={"WWW-Authenticate": "ApiKey"},
            )
        if auth is None or not auth.validate(api_key):
            return JSONResponse(status_code=403, content={"detail": "Invalid API key"})

        request.state.api_key = api_key
        request.state.api_key_fingerprint = auth.fingerprint(api_key)
        return await call_next(request)
