"""Groq LLM provider."""

from __future__ import annotations

import os

from src.layer1_contracts.schemas.health import HealthStatus, ProviderHealth
from src.layer1_contracts.schemas.llm import LLMRequest, LLMResponse
from src.layer4_providers.llms.base import BaseLLMProvider


class GroqProvider(BaseLLMProvider):
    """Groq provider using the OpenAI-compatible API."""

    def __init__(
        self,
        provider_id: str = "groq",
        api_key: str | None = None,
        model: str = "llama-3.1-70b-versatile",
        timeout: float = 30.0,
    ) -> None:
        super().__init__(
            provider_id=provider_id,
            api_key=api_key or os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
            model=model,
            timeout=timeout,
        )

    @property
    def vendor(self) -> str:
        """Return provider vendor."""
        return "groq"

    def supports_model(self, model: str) -> bool:
        """Return whether Groq can serve the requested model."""
        lowered = model.lower()
        return any(token in lowered for token in ("llama", "mixtral", "gemma", "qwen"))

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Execute a chat completion against Groq."""
        return await self._openai_compatible_complete(
            request=request,
            provider_name="Groq",
            headers={"Authorization": f"Bearer {self._api_key}"},
        )

    async def complete_stream(self, request: LLMRequest):
        """Stream Groq completion chunks."""
        async for chunk in self._openai_compatible_stream(
            request=request,
            headers={"Authorization": f"Bearer {self._api_key}"},
        ):
            yield chunk

    async def health_check(self) -> ProviderHealth:
        """Probe the Groq models endpoint for health."""
        if not self.api_key_configured:
            return self._build_health(
                status=HealthStatus.UNHEALTHY,
                is_available=False,
                last_error="API key not configured",
            )
        try:
            response = await self._client.get(
                f"{self._base_url}/models",
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
            if response.status_code == 200:
                return self._build_health(status=HealthStatus.HEALTHY, is_available=True)
            self._record_failure(f"Groq health probe returned {response.status_code}")
            return self._build_health(
                status=HealthStatus.UNHEALTHY,
                is_available=False,
                last_error=f"Health probe returned HTTP {response.status_code}",
            )
        except Exception as error:  # noqa: BLE001
            self._record_failure(f"Groq health probe failed: {error}")
            return self._build_health(
                status=HealthStatus.UNHEALTHY,
                is_available=False,
                last_error=str(error),
            )
