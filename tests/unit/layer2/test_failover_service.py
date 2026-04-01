"""Tests for the failover service facade."""

import pytest

from src.layer1_contracts.schemas.llm import LLMConfig, LLMRequest, Message, MessageRole
from src.layer2_domain.failover.service import FailoverService
from src.layer2_domain.failover.state_machine import FailoverConfig
from src.layer4_providers.llms.mock.provider import MockLLMProvider


@pytest.mark.asyncio
async def test_failover_service_delegates_to_state_machine() -> None:
    """Failover service should execute requests through its provider chain."""
    provider = MockLLMProvider(provider_id="provider-1", random_func=lambda: 0.9, sleep_func=_fake_sleep)
    service = FailoverService(providers=[provider], config=FailoverConfig(max_retries=0))

    response = await service.execute(
        LLMRequest(
            id="req-1",
            messages=[Message(role=MessageRole.USER, content="hi")],
            config=LLMConfig(model="mock-model"),
        )
    )

    assert response.provider == "provider-1"
    assert service.get_attempt_history()[0].success is True


async def _fake_sleep(_: float) -> None:
    """Async no-op."""
