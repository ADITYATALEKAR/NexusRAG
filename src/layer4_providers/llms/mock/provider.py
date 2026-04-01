"""Mock LLM provider used for failover and bootstrap tests."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone
import random

from src.layer0_core.errors.base import ProviderError, RateLimitError, TimeoutError
from src.layer1_contracts.interfaces.llm import LLMProviderInterface
from src.layer1_contracts.schemas.health import HealthStatus, ProviderHealth
from src.layer1_contracts.schemas.llm import LLMRequest, LLMResponse, LLMUsage


class MockLLMProvider(LLMProviderInterface):
    """Configurable mock provider for testing failover behavior."""

    def __init__(
        self,
        provider_id: str,
        vendor: str = "mock",
        model: str = "mock-model",
        failure_rate: float = 0.0,
        rate_limit_rate: float = 0.0,
        timeout_rate: float = 0.0,
        base_latency_ms: int = 100,
        response_template: str = "Mock response from {provider_id}",
        random_func=None,
        sleep_func=None,
    ) -> None:
        self._provider_id = provider_id
        self._vendor = vendor
        self._model = model
        self._failure_rate = failure_rate
        self._rate_limit_rate = rate_limit_rate
        self._timeout_rate = timeout_rate
        self._base_latency_ms = base_latency_ms
        self._response_template = response_template
        self._healthy = True
        self._last_error: str | None = None
        self._total_latency_ms = 0
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self._random_func = random_func or random.random
        self._sleep_func = sleep_func or asyncio.sleep

    @property
    def provider_id(self) -> str:
        """Return provider id."""
        return self._provider_id

    @property
    def vendor(self) -> str:
        """Return vendor name."""
        return self._vendor

    @property
    def model(self) -> str:
        """Return model name."""
        return self._model

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Return a mock LLM response or raise a simulated provider error."""
        self.total_requests += 1
        await self._sleep_func(self._base_latency_ms / 1000)

        if not self._healthy:
            self.failed_requests += 1
            self._last_error = "provider marked unhealthy"
            raise ProviderError("Mock provider is unhealthy", provider_id=self.provider_id)

        roll = self._random_func()
        if roll < self._timeout_rate:
            self.failed_requests += 1
            self._last_error = "timeout"
            raise TimeoutError(
                "Mock timeout",
                timeout_seconds=request.timeout_seconds,
            )
        if roll < self._timeout_rate + self._rate_limit_rate:
            self.failed_requests += 1
            self._last_error = "rate limited"
            raise RateLimitError("Mock rate limited", retry_after=5.0)
        if roll < self._timeout_rate + self._rate_limit_rate + self._failure_rate:
            self.failed_requests += 1
            self._last_error = "provider error"
            raise ProviderError("Mock provider error", provider_id=self.provider_id)

        self.successful_requests += 1
        self._last_error = None
        prompt_tokens = sum(len(message.content.split()) for message in request.messages)
        completion_tokens = max(1, min(request.config.max_tokens, 16))
        self._total_latency_ms += self._base_latency_ms
        return LLMResponse(
            request_id=request.id,
            content=self._response_template.format(provider_id=self.provider_id),
            provider=self.provider_id,
            model=self.model,
            usage=LLMUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            latency_ms=self._base_latency_ms,
            finish_reason="stop",
            providers_attempted=[self.provider_id],
        )

    async def complete_stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Stream the mock response in a single chunk."""
        response = await self.complete(request)
        yield response.content

    async def health_check(self) -> ProviderHealth:
        """Return current provider health."""
        avg_latency = None
        if self.successful_requests:
            avg_latency = self._total_latency_ms / self.successful_requests
        status = HealthStatus.HEALTHY
        if not self._healthy:
            status = HealthStatus.UNHEALTHY
        elif self.failed_requests > 0:
            status = HealthStatus.DEGRADED
        cooldown_until = None
        return ProviderHealth(
            provider_id=self.provider_id,
            provider_type="llm",
            vendor=self.vendor,
            status=status,
            is_available=self._healthy,
            is_in_cooldown=False,
            cooldown_until=cooldown_until,
            total_requests=self.total_requests,
            successful_requests=self.successful_requests,
            failed_requests=self.failed_requests,
            avg_latency_ms=avg_latency,
            last_error=self._last_error,
        )

    def set_failure_rate(self, rate: float) -> None:
        """Update the provider failure rate."""
        self._failure_rate = rate

    def set_rate_limit_rate(self, rate: float) -> None:
        """Update the provider rate limit rate."""
        self._rate_limit_rate = rate

    def set_timeout_rate(self, rate: float) -> None:
        """Update the provider timeout rate."""
        self._timeout_rate = rate

    def set_healthy(self, healthy: bool) -> None:
        """Mark the provider healthy or unhealthy."""
        self._healthy = healthy
