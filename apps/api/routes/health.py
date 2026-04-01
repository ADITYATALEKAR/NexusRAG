"""Health and readiness routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from src.layer1_contracts.schemas.health import HealthStatus, SystemHealth

router = APIRouter()


@router.get("/liveness")
async def liveness() -> dict[str, str]:
    """Return 200 when the process is alive."""
    return {"status": "alive"}


@router.get("/readiness")
async def readiness(request: Request) -> dict[str, str]:
    """Return 200 only when bootstrap is complete and providers are available."""
    startup_result = getattr(request.app.state, "startup_result", None)
    if startup_result is None or not startup_result.ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="System is not ready",
        )
    return {"status": "ready"}


@router.get("/", response_model=SystemHealth)
@router.get("", response_model=SystemHealth, include_in_schema=False)
async def health(request: Request) -> SystemHealth:
    """Return the current system health snapshot."""
    startup_result = getattr(request.app.state, "startup_result", None)
    if startup_result is None:
        return SystemHealth(status=HealthStatus.UNKNOWN)
    startup_result.system_health.providers = list(
        (await startup_result.provider_registry.refresh_all_health()).values()
    )
    return startup_result.system_health
