"""LLM provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from src.layer1_contracts.schemas.health import ProviderHealth
from src.layer1_contracts.schemas.llm import LLMRequest, LLMResponse


class LLMProviderInterface(ABC):
    """All LLM providers must implement this interface."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Return the provider identifier."""

    @property
    @abstractmethod
    def vendor(self) -> str:
        """Return the provider vendor."""

    @property
    @abstractmethod
    def model(self) -> str:
        """Return the model name."""

    @abstractmethod
    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Execute a completion request."""

    @abstractmethod
    async def complete_stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Stream completion chunks."""

    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        """Return provider health."""
