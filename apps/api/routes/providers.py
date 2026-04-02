"""Provider health routes."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, status

from src.layer2_domain.failover.service import FailoverService
from src.layer2_domain.failover.state_machine import FailoverConfig as DomainFailoverConfig
from src.layer1_contracts.schemas.health import ProviderHealth
from src.layer4_providers.llms.registry import build_configured_providers, load_provider_config
from src.layer5_wiring.registry.provider_registry import ProviderRegistry
from src.layer8_runtime.config.loader import ConfigLoader
from src.layer8_runtime.config.schemas import FailoverFileConfig

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
        diagnostics_runtime = await _get_or_build_provider_diagnostics_runtime(request)
        return diagnostics_runtime
    except HTTPException:
        return None, None
    except Exception:  # noqa: BLE001
        return None, None


async def _get_or_build_provider_diagnostics_runtime(request: Request):
    """Build a lightweight provider-only runtime for health routes."""
    provider_registry = getattr(request.app.state, "provider_diagnostics_registry", None)
    failover_service = getattr(request.app.state, "provider_diagnostics_failover_service", None)
    if provider_registry is not None and failover_service is not None:
        return provider_registry, failover_service

    config_dir = Path(__file__).resolve().parents[3] / "configs"
    loader = ConfigLoader(config_dir=config_dir)
    provider_raw = load_provider_config(config_dir)
    failover_file_config = loader.load_validated(
        "models/llm-failover.yaml",
        FailoverFileConfig,
        apply_env_overrides=False,
    )

    provider_registry = ProviderRegistry()
    providers = build_configured_providers(provider_raw)
    if not providers:
        request.app.state.provider_diagnostics_registry = provider_registry
        request.app.state.provider_diagnostics_failover_service = FailoverService(
            [],
            DomainFailoverConfig(),
        )
        return provider_registry, request.app.state.provider_diagnostics_failover_service

    for provider in providers:
        await provider_registry.register(provider, check_health=False)

    failover_service = FailoverService(
        providers=provider_registry.get_all(),
        config=DomainFailoverConfig(
            max_retries=failover_file_config.failover.retry.max_retries,
            base_delay_seconds=failover_file_config.failover.retry.base_delay_seconds,
            max_delay_seconds=failover_file_config.failover.retry.max_delay_seconds,
            backoff_multiplier=failover_file_config.failover.retry.backoff_multiplier,
            jitter=failover_file_config.failover.retry.jitter,
            cooldown_duration_seconds=failover_file_config.failover.cooldown.default_duration_seconds,
            max_cooldown_duration_seconds=failover_file_config.failover.cooldown.max_duration_seconds,
            consecutive_failures_threshold=failover_file_config.failover.cooldown.consecutive_failures_threshold,
        ),
    )

    request.app.state.provider_diagnostics_registry = provider_registry
    request.app.state.provider_diagnostics_failover_service = failover_service
    return provider_registry, failover_service


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
