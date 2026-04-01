"""Failover service."""

from __future__ import annotations

from src.layer0_core.time.clock import Clock
from src.layer1_contracts.interfaces.llm import LLMProviderInterface
from src.layer1_contracts.schemas.llm import LLMRequest, LLMResponse
from src.layer2_domain.failover.state_machine import FailoverConfig, FailoverStateMachine


class FailoverService:
    """High-level facade over the failover state machine."""

    def __init__(
        self,
        providers: list[LLMProviderInterface],
        config: FailoverConfig,
        clock: Clock | None = None,
    ) -> None:
        self._machine = FailoverStateMachine(providers=providers, config=config, clock=clock)

    def set_providers(self, providers: list[LLMProviderInterface]) -> None:
        """Replace the provider chain."""
        self._machine.providers = list(providers)

    async def execute(self, request: LLMRequest) -> LLMResponse:
        """Execute a request with failover."""
        return await self._machine.execute(request)

    def get_attempt_history(self):
        """Return provider attempt history."""
        return self._machine.get_attempt_history()

    def get_cooldown_status(self):
        """Return provider cooldown states."""
        return self._machine.get_cooldown_status()
