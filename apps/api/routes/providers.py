"""Provider health routes."""

from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, HTTPException, Request, status

from src.layer1_contracts.schemas.health import ProviderHealth

router = APIRouter()


@router.get("/health", response_model=list[ProviderHealth])
async def provider_health(request: Request) -> list[ProviderHealth]:
    """Return health for all providers."""
    provider_registry, failover_service = await _get_provider_runtime(request)
    if provider_registry is None:
        return []
    health = await provider_registry.refresh_all_health()
    return _apply_cooldowns(list(health.values()), failover_service)


@router.get("/{provider_id}/health", response_model=ProviderHealth)
async def single_provider_health(request: Request, provider_id: str) -> ProviderHealth:
    """Return health for one provider."""
    provider_registry, failover_service = await _get_provider_runtime(request)
    if provider_registry is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="System not ready")
    health_map = await provider_registry.refresh_all_health()
    health = health_map.get(provider_id) or provider_registry.get_health(provider_id)
    if health is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    return _apply_cooldowns([health], failover_service)[0]


async def _get_provider_runtime(request: Request):
    """Resolve the Phase 4 answer-provider runtime for management routes."""
    provider_registry = getattr(request.app.state, "answer_provider_registry", None)
    failover_service = getattr(request.app.state, "answer_failover_service", None)
    if provider_registry is not None and failover_service is not None:
        return provider_registry, failover_service

    try:
        from apps.api.routes.answer import _get_or_build_answer_runtime

        runtime = await _get_or_build_answer_runtime(request)
        return runtime.provider_registry, runtime.failover_service
    except HTTPException:
        return None, None


def _apply_cooldowns(
    health_items: list[ProviderHealth],
    failover_service,
) -> list[ProviderHealth]:
    """Overlay failover cooldown state onto provider health entries."""
    if failover_service is None:
        return health_items
    cooldowns = failover_service.get_cooldown_status()
    updated: list[ProviderHealth] = []
    for health in health_items:
        cooldown = cooldowns.get(health.provider_id)
        if cooldown is None:
            updated.append(health)
            continue
        updated.append(
            health.model_copy(
                update={
                    "is_in_cooldown": True,
                    "cooldown_until": cooldown.started_at + timedelta(seconds=cooldown.duration_seconds),
                }
            )
        )
    return updated
