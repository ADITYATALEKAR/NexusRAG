"""Tests for the failover state machine."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime, timezone

import pytest

from src.layer0_core.enums.errors import ErrorCategory
from src.layer0_core.errors.base import RAGBaseError
from src.layer0_core.time.clock import MockClock
from src.layer1_contracts.interfaces.llm import LLMProviderInterface
from src.layer1_contracts.schemas.health import HealthStatus, ProviderHealth
from src.layer1_contracts.schemas.llm import LLMConfig, LLMRequest, LLMResponse, LLMUsage, Message, MessageRole
from src.layer2_domain.failover.state_machine import FailoverConfig, FailoverStateMachine
from src.layer4_providers.llms.mock.provider import MockLLMProvider


class TransientProvider(LLMProviderInterface):
    """Provider that fails transiently before succeeding."""

    def __init__(self) -> None:
        self.attempts = 0

    @property
    def provider_id(self) -> str:
        return "transient-provider"

    @property
    def vendor(self) -> str:
        return "mock"

    @property
    def model(self) -> str:
        return "mock-model"

    async def complete(self, request: LLMRequest) -> LLMResponse:
        self.attempts += 1
        if self.attempts < 3:
            raise RAGBaseError("temporary", category=ErrorCategory.TRANSIENT)
        return LLMResponse(
            request_id=request.id,
            content="ok",
            provider=self.provider_id,
            model=self.model,
            usage=LLMUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
            latency_ms=1,
            finish_reason="stop",
        )

    async def complete_stream(self, request: LLMRequest) -> AsyncIterator[str]:
        yield "ok"

    async def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            provider_id=self.provider_id,
            provider_type="llm",
            vendor=self.vendor,
            status=HealthStatus.HEALTHY,
        )


def make_request() -> LLMRequest:
    """Build a simple LLM request."""
    return LLMRequest(
        id="req-1",
        messages=[Message(role=MessageRole.USER, content="hello")],
        config=LLMConfig(model="mock-model"),
    )


@pytest.mark.asyncio
async def test_failover_uses_next_provider_on_provider_error() -> None:
    """A failing provider should fail over to the next healthy provider."""
    failing = MockLLMProvider(
        provider_id="provider-1",
        failure_rate=1.0,
        random_func=lambda: 0.5,
        sleep_func=lambda _: _noop(),
    )
    healthy = MockLLMProvider(
        provider_id="provider-2",
        random_func=lambda: 0.9,
        sleep_func=lambda _: _noop(),
    )
    machine = FailoverStateMachine(
        providers=[failing, healthy],
        config=FailoverConfig(max_retries=0),
        clock=MockClock(datetime(2024, 1, 1, tzinfo=timezone.utc)),
    )

    response = await machine.execute(make_request())

    assert response.provider == "provider-2"
    assert len(machine.get_attempt_history()) == 2


@pytest.mark.asyncio
async def test_failover_retries_with_backoff_on_transient_errors() -> None:
    """Transient errors should retry with exponential backoff."""
    delays: list[float] = []

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    machine = FailoverStateMachine(
        providers=[TransientProvider()],
        config=FailoverConfig(max_retries=2, jitter=False, base_delay_seconds=1.0),
        clock=MockClock(datetime(2024, 1, 1, tzinfo=timezone.utc)),
        sleep_func=fake_sleep,
    )

    response = await machine.execute(make_request())

    assert response.provider == "transient-provider"
    assert delays == [1.0, 2.0]


@pytest.mark.asyncio
async def test_failover_enters_cooldown_after_rate_limit() -> None:
    """Rate-limited providers should be placed into cooldown."""
    limited = MockLLMProvider(
        provider_id="provider-1",
        rate_limit_rate=1.0,
        random_func=lambda: 0.1,
        sleep_func=lambda _: _noop(),
    )
    healthy = MockLLMProvider(
        provider_id="provider-2",
        random_func=lambda: 0.9,
        sleep_func=lambda _: _noop(),
    )
    machine = FailoverStateMachine(
        providers=[limited, healthy],
        config=FailoverConfig(max_retries=0, cooldown_duration_seconds=30),
        clock=MockClock(datetime(2024, 1, 1, tzinfo=timezone.utc)),
    )

    response = await machine.execute(make_request())

    assert response.provider == "provider-2"
    assert "provider-1" in machine.get_cooldown_status()


async def _noop() -> None:
    """Async no-op helper."""
