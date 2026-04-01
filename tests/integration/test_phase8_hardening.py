"""Integration tests for Phase 8 middleware hardening."""

from __future__ import annotations

import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from apps.api.middleware.cors import configure_cors
from apps.api.lifespan import ShutdownCoordinator
from apps.api.middleware.rate_limit import RateLimitMiddleware
from apps.api.middleware.security import SecurityHeadersMiddleware
from src.layer6_security.auth.api_key import APIKeyAuth
from src.layer6_security.auth.middleware import AuthMiddleware
from src.layer6_security.rate_limiting.backends import MemoryBackend
from src.layer6_security.rate_limiting.limiter import RateLimiter


def _build_secured_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(AuthMiddleware, auth=APIKeyAuth(["valid-key"]), enabled=True)
    app.add_middleware(
        RateLimitMiddleware,
        limiter=RateLimiter(MemoryBackend(), requests_per_minute=1, requests_per_hour=10),
        enabled=True,
    )
    app.add_middleware(SecurityHeadersMiddleware)
    configure_cors(app, origins=["http://localhost:3000"], allow_credentials=True)

    @app.get("/protected")
    async def protected() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/liveness")
    async def liveness() -> dict[str, str]:
        return {"status": "alive"}

    return app


def test_missing_or_invalid_api_key_is_rejected() -> None:
    """Protected endpoints should reject missing and invalid API keys."""
    with TestClient(_build_secured_app()) as client:
        missing = client.get("/protected")
        assert missing.status_code == 401

        invalid = client.get("/protected", headers={"X-API-Key": "wrong"})
        assert invalid.status_code == 403


def test_rate_limit_and_security_headers_are_applied() -> None:
    """Valid requests should receive headers and over-limit requests should be blocked."""
    with TestClient(_build_secured_app()) as client:
        allowed = client.get("/protected", headers={"X-API-Key": "valid-key"})
        assert allowed.status_code == 200
        assert allowed.headers["X-RateLimit-Limit"] == "1"
        assert allowed.headers["X-Content-Type-Options"] == "nosniff"
        assert allowed.headers["X-Frame-Options"] == "DENY"
        assert allowed.headers["Content-Security-Policy"] == "default-src 'self'"

        blocked = client.get("/protected", headers={"X-API-Key": "valid-key"})
        assert blocked.status_code == 429
        assert blocked.headers["Retry-After"]


def test_cors_and_health_exclusions_work() -> None:
    """Health checks should bypass auth/rate limit, and CORS should respond to preflight."""
    with TestClient(_build_secured_app()) as client:
        liveness = client.get("/health/liveness")
        assert liveness.status_code == 200
        assert liveness.headers["X-RateLimit-Limit"] == "1"
        assert liveness.headers["X-RateLimit-Remaining"] == "1"
        assert liveness.headers["X-RateLimit-Reset"]

        preflight = client.options(
            "/protected",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert preflight.status_code == 200
        assert preflight.headers["access-control-allow-origin"] == "http://localhost:3000"


@pytest.mark.asyncio
async def test_shutdown_coordinator_waits_for_inflight_requests() -> None:
    """Shutdown should wait for active requests to finish before completing."""
    coordinator = ShutdownCoordinator()
    request_started = asyncio.Event()
    release_request = asyncio.Event()

    async def inflight_request() -> None:
        await coordinator.request_started()
        request_started.set()
        try:
            await release_request.wait()
        finally:
            await coordinator.request_finished()

    task = asyncio.create_task(inflight_request())
    await request_started.wait()

    await coordinator.start_shutdown()
    wait_task = asyncio.create_task(coordinator.wait_for_idle(timeout_seconds=0.25))
    await asyncio.sleep(0.05)
    assert wait_task.done() is False
    assert coordinator.active_requests == 1

    release_request.set()
    assert await wait_task is True
    await task
    assert coordinator.active_requests == 0
