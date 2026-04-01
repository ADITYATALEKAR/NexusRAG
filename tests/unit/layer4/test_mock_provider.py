"""Tests for the mock provider."""

import pytest

from src.layer1_contracts.schemas.llm import LLMConfig, LLMRequest, Message, MessageRole
from src.layer4_providers.llms.mock.provider import MockLLMProvider


@pytest.mark.asyncio
async def test_mock_provider_tracks_statistics() -> None:
    """Successful calls should update provider stats."""
    provider = MockLLMProvider(provider_id="mock-1", random_func=lambda: 0.9, sleep_func=_fake_sleep)
    request = LLMRequest(
        id="req-1",
        messages=[Message(role=MessageRole.USER, content="hello world")],
        config=LLMConfig(model="mock-model"),
    )

    response = await provider.complete(request)
    health = await provider.health_check()

    assert response.provider == "mock-1"
    assert health.total_requests == 1
    assert health.successful_requests == 1


@pytest.mark.asyncio
async def test_mock_provider_can_be_marked_unhealthy() -> None:
    """Unhealthy providers should raise provider errors."""
    provider = MockLLMProvider(provider_id="mock-1", random_func=lambda: 0.9, sleep_func=_fake_sleep)
    provider.set_healthy(False)
    request = LLMRequest(
        id="req-1",
        messages=[Message(role=MessageRole.USER, content="hello")],
        config=LLMConfig(model="mock-model"),
    )

    with pytest.raises(Exception):
        await provider.complete(request)


async def _fake_sleep(_: float) -> None:
    """Async no-op."""
