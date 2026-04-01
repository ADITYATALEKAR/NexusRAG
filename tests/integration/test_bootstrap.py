"""Integration tests for bootstrap and API startup."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from apps.api.main import app
from apps.api.routes.health import router as health_router
from src.layer8_runtime.bootstrap.startup import BootstrapSequence


@pytest.mark.asyncio
async def test_bootstrap_sequence_runs_successfully() -> None:
    """Bootstrap should produce a ready startup result with ordered components."""
    sequence = BootstrapSequence(config_dir=Path("configs"))

    result = await sequence.run()

    assert result.ready is True
    assert "config_loader" in result.initialization_order
    assert result.provider_registry.count() >= 1


def test_api_health_routes_before_and_after_bootstrap() -> None:
    """Readiness should be 503 before bootstrap and 200 after lifespan startup."""
    preboot_app = FastAPI()
    preboot_app.include_router(health_router, prefix="/health")
    preboot_client = TestClient(preboot_app)

    preboot_response = preboot_client.get("/health/readiness")
    assert preboot_response.status_code == 503

    with TestClient(app) as client:
        assert client.get("/health/liveness").status_code == 200
        assert client.get("/health/readiness").status_code == 200
        assert client.get("/health/").status_code == 200
        assert client.get("/providers/health").status_code == 200
        assert client.get("/wiring/graph").status_code == 200
