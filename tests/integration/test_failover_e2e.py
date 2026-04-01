"""End-to-end failover tests."""

from pathlib import Path

import pytest

from src.layer1_contracts.schemas.llm import LLMConfig, LLMRequest, Message, MessageRole
from src.layer4_providers.llms.mock.provider import MockLLMProvider
from src.layer8_runtime.bootstrap.startup import BootstrapSequence


@pytest.mark.asyncio
async def test_failover_uses_backup_provider_when_primary_fails() -> None:
    """Configured failover chain should move from a failing primary to a backup provider."""
    result = await BootstrapSequence(config_dir=Path("configs")).run()
    providers = result.provider_registry.get_all()
    assert len(providers) >= 2

    primary = providers[0]
    backup = providers[1]
    assert isinstance(primary, MockLLMProvider)
    assert isinstance(backup, MockLLMProvider)
    primary.set_failure_rate(1.0)

    response = await result.failover_service.execute(
        LLMRequest(
            id="req-1",
            messages=[Message(role=MessageRole.USER, content="hello")],
            config=LLMConfig(model="mock-model"),
        )
    )

    assert response.provider == backup.provider_id
    assert result.failover_service.get_attempt_history()
