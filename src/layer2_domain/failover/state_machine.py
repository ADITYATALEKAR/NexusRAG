"""Failover state machine."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import random

from src.layer0_core.enums.errors import ErrorCategory, RetryDecision
from src.layer0_core.errors.base import ProviderError
from src.layer0_core.time.clock import Clock, SystemClock
from src.layer1_contracts.interfaces.llm import LLMProviderInterface
from src.layer1_contracts.schemas.llm import LLMRequest, LLMResponse
from src.layer2_domain.failover.error_classifier import ErrorClassifier


class FailoverState(str, Enum):
    """Failover execution states."""

    IDLE = "idle"
    ATTEMPTING = "attempting"
    RETRYING = "retrying"
    FAILING_OVER = "failing_over"
    SUCCEEDED = "succeeded"
    EXHAUSTED = "exhausted"


@dataclass
class ProviderAttempt:
    """Record of one provider attempt."""

    provider_id: str
    started_at: datetime
    ended_at: datetime | None = None
    success: bool = False
    error: str | None = None
    error_category: ErrorCategory | None = None
    latency_ms: int | None = None


@dataclass
class CooldownState:
    """Provider cooldown state."""

    provider_id: str
    started_at: datetime
    duration_seconds: int
    reason: str

    def is_active(self, now: datetime) -> bool:
        """Return whether cooldown is still active."""
        return now < self.started_at + timedelta(seconds=self.duration_seconds)

    def remaining_seconds(self, now: datetime) -> float:
        """Return remaining cooldown time in seconds."""
        remaining = (self.started_at + timedelta(seconds=self.duration_seconds) - now).total_seconds()
        return max(0.0, remaining)


@dataclass
class FailoverConfig:
    """Failover timing and cooldown settings."""

    max_retries: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0
    backoff_multiplier: float = 2.0
    jitter: bool = True
    cooldown_duration_seconds: int = 60
    max_cooldown_duration_seconds: int = 300
    consecutive_failures_threshold: int = 3


class FailoverStateMachine:
    """Execute requests with retry, failover, and provider cooldown support."""

    def __init__(
        self,
        providers: list[LLMProviderInterface],
        config: FailoverConfig,
        clock: Clock | None = None,
        sleep_func: Callable[[float], Awaitable[None]] | None = None,
        random_func: Callable[[], float] | None = None,
    ) -> None:
        self.providers = list(providers)
        self.config = config
        self.clock = clock or SystemClock()
        self.sleep_func = sleep_func or asyncio.sleep
        self.random_func = random_func or random.random
        self.state = FailoverState.IDLE
        self._attempt_history: list[ProviderAttempt] = []
        self._cooldowns: dict[str, CooldownState] = {}
        self._consecutive_failures: dict[str, int] = {provider.provider_id: 0 for provider in providers}

    async def execute(self, request: LLMRequest) -> LLMResponse:
        """Execute a request across the provider chain."""
        self._attempt_history = []
        self.state = FailoverState.ATTEMPTING
        ordered_providers = self._ordered_providers(request)
        attempted_provider_ids: list[str] = []
        last_error: Exception | None = None

        for provider in ordered_providers:
            if self._is_in_cooldown(provider.provider_id):
                continue

            attempted_provider_ids.append(provider.provider_id)
            provider_response = await self._execute_with_retries(provider, request)
            if isinstance(provider_response, LLMResponse):
                provider_response.providers_attempted = attempted_provider_ids.copy()
                provider_response.failover_occurred = len(attempted_provider_ids) > 1
                self.state = FailoverState.SUCCEEDED
                self._consecutive_failures[provider.provider_id] = 0
                return provider_response

            last_error = provider_response
            decision = ErrorClassifier.classify(provider_response)[1]
            if decision == RetryDecision.ABORT:
                self.state = FailoverState.EXHAUSTED
                raise provider_response
            self.state = FailoverState.FAILING_OVER

        self.state = FailoverState.EXHAUSTED
        if last_error is not None:
            raise last_error
        raise ProviderError(
            "No providers available to satisfy request",
            provider_id=request.preferred_provider or "unknown",
        )

    def get_attempt_history(self) -> list[ProviderAttempt]:
        """Return provider attempt history."""
        return list(self._attempt_history)

    def get_cooldown_status(self) -> dict[str, CooldownState]:
        """Return active cooldown states."""
        now = self.clock.now()
        return {
            provider_id: cooldown
            for provider_id, cooldown in self._cooldowns.items()
            if cooldown.is_active(now)
        }

    async def _execute_with_retries(
        self, provider: LLMProviderInterface, request: LLMRequest
    ) -> LLMResponse | Exception:
        """Execute against one provider with retries."""
        for attempt_number in range(self.config.max_retries + 1):
            if attempt_number > 0:
                self.state = FailoverState.RETRYING

            attempt = ProviderAttempt(provider_id=provider.provider_id, started_at=self.clock.now())
            self._attempt_history.append(attempt)
            start_ms = self.clock.now_ms()

            try:
                response = await provider.complete(request)
                attempt.ended_at = self.clock.now()
                attempt.success = True
                attempt.latency_ms = max(0, self.clock.now_ms() - start_ms)
                self._consecutive_failures[provider.provider_id] = 0
                return response
            except Exception as error:  # noqa: BLE001
                category, decision = ErrorClassifier.classify(error)
                attempt.ended_at = self.clock.now()
                attempt.error = str(error)
                attempt.error_category = category
                attempt.latency_ms = max(0, self.clock.now_ms() - start_ms)
                self._consecutive_failures[provider.provider_id] = (
                    self._consecutive_failures.get(provider.provider_id, 0) + 1
                )

                if decision == RetryDecision.RETRY_BACKOFF and attempt_number < self.config.max_retries:
                    await self.sleep_func(self._calculate_backoff(attempt_number))
                    continue

                if decision == RetryDecision.COOLDOWN_FAILOVER:
                    self._enter_cooldown(
                        provider.provider_id,
                        reason=str(error),
                        requested_seconds=getattr(error, "retry_after", None),
                    )
                    return error

                if self._consecutive_failures[provider.provider_id] >= (
                    self.config.consecutive_failures_threshold
                ):
                    self._enter_cooldown(provider.provider_id, reason=str(error))

                if decision == RetryDecision.RETRY_SAME and attempt_number < self.config.max_retries:
                    continue

                return error

        return ProviderError("Provider retries exhausted", provider_id=provider.provider_id)

    def _ordered_providers(self, request: LLMRequest) -> list[LLMProviderInterface]:
        """Order providers using the preferred provider when provided."""
        providers = list(self.providers)
        if request.preferred_provider:
            providers.sort(key=lambda provider: provider.provider_id != request.preferred_provider)
            if not request.fallback_allowed:
                providers = [
                    provider
                    for provider in providers
                    if provider.provider_id == request.preferred_provider
                ]
        return providers

    def _calculate_backoff(self, attempt_number: int) -> float:
        """Calculate exponential backoff delay."""
        delay = min(
            self.config.base_delay_seconds
            * (self.config.backoff_multiplier ** attempt_number),
            self.config.max_delay_seconds,
        )
        if self.config.jitter:
            delay *= 0.5 + self.random_func()
        return delay

    def _is_in_cooldown(self, provider_id: str) -> bool:
        """Return whether the provider is currently cooling down."""
        cooldown = self._cooldowns.get(provider_id)
        if cooldown is None:
            return False
        if not cooldown.is_active(self.clock.now()):
            self._cooldowns.pop(provider_id, None)
            return False
        return True

    def _enter_cooldown(
        self, provider_id: str, reason: str, requested_seconds: float | None = None
    ) -> None:
        """Put a provider into cooldown."""
        duration = int(requested_seconds or self.config.cooldown_duration_seconds)
        duration = max(1, min(duration, self.config.max_cooldown_duration_seconds))
        self._cooldowns[provider_id] = CooldownState(
            provider_id=provider_id,
            started_at=self.clock.now(),
            duration_seconds=duration,
            reason=reason,
        )
