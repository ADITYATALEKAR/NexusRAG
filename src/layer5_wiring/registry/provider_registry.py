"""Provider registry with health caching."""

from __future__ import annotations

import asyncio

from src.layer0_core.errors.base import WiringError
from src.layer1_contracts.interfaces.llm import LLMProviderInterface
from src.layer1_contracts.schemas.health import HealthStatus, ProviderHealth


class ProviderRegistry:
    """Central registry for providers with health tracking."""

    def __init__(self) -> None:
        self._providers: dict[str, LLMProviderInterface] = {}
        self._health_cache: dict[str, ProviderHealth] = {}
        self._registration_order: list[str] = []
        self._lock = asyncio.Lock()

    async def register(self, provider: LLMProviderInterface, check_health: bool = True) -> None:
        """Register a provider and optionally refresh its health."""
        async with self._lock:
            if provider.provider_id in self._providers:
                raise WiringError(f"Provider already registered: {provider.provider_id}")

            self._providers[provider.provider_id] = provider
            self._registration_order.append(provider.provider_id)

            if check_health:
                try:
                    self._health_cache[provider.provider_id] = await provider.health_check()
                except Exception as error:  # noqa: BLE001
                    self._health_cache[provider.provider_id] = ProviderHealth(
                        provider_id=provider.provider_id,
                        provider_type="llm",
                        vendor=provider.vendor,
                        status=HealthStatus.UNHEALTHY,
                        is_available=False,
                        last_error=str(error),
                    )

    async def unregister(self, provider_id: str) -> None:
        """Unregister a provider."""
        async with self._lock:
            if provider_id in self._providers:
                del self._providers[provider_id]
                self._registration_order.remove(provider_id)
                self._health_cache.pop(provider_id, None)

    def get(self, provider_id: str) -> LLMProviderInterface | None:
        """Return one provider."""
        return self._providers.get(provider_id)

    def get_by_vendor(self, vendor: str) -> list[LLMProviderInterface]:
        """Return providers for a vendor."""
        return [provider for provider in self._providers.values() if provider.vendor == vendor]

    def get_all(self) -> list[LLMProviderInterface]:
        """Return providers in registration order."""
        return [self._providers[provider_id] for provider_id in self._registration_order]

    def get_available(self) -> list[LLMProviderInterface]:
        """Return currently healthy providers."""
        available: list[LLMProviderInterface] = []
        for provider_id in self._registration_order:
            provider = self._providers.get(provider_id)
            health = self._health_cache.get(provider_id)
            if provider and health and health.is_available and health.status in {
                HealthStatus.HEALTHY,
                HealthStatus.DEGRADED,
            }:
                available.append(provider)
        return available

    def get_health(self, provider_id: str) -> ProviderHealth | None:
        """Return cached provider health."""
        return self._health_cache.get(provider_id)

    async def update_health(self, provider_id: str, health: ProviderHealth) -> None:
        """Update cached health for a provider."""
        async with self._lock:
            self._health_cache[provider_id] = health

    async def refresh_all_health(self) -> dict[str, ProviderHealth]:
        """Refresh health for all registered providers."""
        results: dict[str, ProviderHealth] = {}
        for provider_id, provider in self._providers.items():
            try:
                health = await provider.health_check()
            except Exception as error:  # noqa: BLE001
                health = ProviderHealth(
                    provider_id=provider_id,
                    provider_type="llm",
                    vendor=provider.vendor,
                    status=HealthStatus.UNHEALTHY,
                    is_available=False,
                    last_error=str(error),
                )
            self._health_cache[provider_id] = health
            results[provider_id] = health
        return results

    def count(self) -> int:
        """Return number of registered providers."""
        return len(self._providers)

    def is_registered(self, provider_id: str) -> bool:
        """Return whether a provider is registered."""
        return provider_id in self._providers
