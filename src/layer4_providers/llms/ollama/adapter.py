"""Ollama local LLM provider."""

from __future__ import annotations

import json
import time

import httpx

from src.layer0_core.errors import ProviderError, TimeoutError
from src.layer1_contracts.schemas.health import HealthStatus, ProviderHealth
from src.layer1_contracts.schemas.llm import (
    LLMRequest,
    LLMResponse,
    LLMUsage,
    Message,
    MessageRole,
)
from src.layer4_providers.llms.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Ollama local inference provider."""

    def __init__(
        self,
        provider_id: str = "ollama",
        base_url: str = "http://localhost:11434",
        model: str = "llama3.1",
        timeout: float = 120.0,
    ) -> None:
        super().__init__(
            provider_id=provider_id,
            api_key="ollama-local",
            base_url=base_url,
            model=model,
            timeout=timeout,
        )

    @property
    def vendor(self) -> str:
        """Return provider vendor."""
        return "ollama"

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Execute a generation request against Ollama."""
        self.total_requests += 1
        started_at = time.perf_counter()
        prompt = self._messages_to_prompt(request.messages)
        payload = {
            "model": self._resolve_model(request.config.model),
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": request.config.temperature,
                "num_predict": request.config.max_tokens,
            },
        }
        try:
            response = await self._client.post(
                f"{self._base_url}/api/generate",
                json=payload,
                timeout=request.timeout_seconds,
            )
            response_body = response.json()
            if response.status_code != 200:
                self._record_failure(f"Ollama HTTP {response.status_code}")
                self._handle_error(response.status_code, response_body, "Ollama")
            latency_ms = int((time.perf_counter() - started_at) * 1000)
            self._record_success(latency_ms)
            prompt_tokens = int(response_body.get("prompt_eval_count", max(1, len(prompt.split()) * 2)))
            completion_tokens = int(
                response_body.get("eval_count", max(1, len(str(response_body.get("response", "")).split()) * 2))
            )
            return LLMResponse(
                request_id=request.id,
                content=str(response_body.get("response", "")),
                provider=self.provider_id,
                model=str(response_body.get("model", self._resolve_model(request.config.model))),
                usage=LLMUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                ),
                latency_ms=latency_ms,
                finish_reason="stop" if response_body.get("done", True) else "length",
            )
        except httpx.TimeoutException as error:
            self._record_failure("Ollama request timed out")
            raise TimeoutError(
                "Ollama request timed out",
                timeout_seconds=request.timeout_seconds,
                cause=error,
            ) from error
        except httpx.HTTPError as error:
            self._record_failure("Ollama request failed")
            raise ProviderError(
                "Ollama request failed",
                provider_id=self.provider_id,
                cause=error,
            ) from error

    async def complete_stream(self, request: LLMRequest):
        """Stream tokens from Ollama's NDJSON generation endpoint."""
        prompt = self._messages_to_prompt(request.messages)
        payload = {
            "model": self._resolve_model(request.config.model),
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": request.config.temperature,
                "num_predict": request.config.max_tokens,
            },
        }
        async with self._client.stream(
            "POST",
            f"{self._base_url}/api/generate",
            json=payload,
            timeout=request.timeout_seconds,
        ) as response:
            if response.status_code != 200:
                body = await response.aread()
                self._record_failure(f"Ollama HTTP {response.status_code}")
                self._handle_error(
                    response.status_code,
                    {"error": body.decode("utf-8", errors="ignore")},
                    "Ollama",
                )
            async for line in response.aiter_lines():
                if not line:
                    continue
                data = json.loads(line)
                if "response" in data:
                    yield str(data["response"])

    async def health_check(self) -> ProviderHealth:
        """Probe the local Ollama tags endpoint for health."""
        try:
            response = await self._client.get(f"{self._base_url}/api/tags")
            if response.status_code == 200:
                return self._build_health(status=HealthStatus.HEALTHY, is_available=True)
            self._record_failure(f"Ollama health probe returned {response.status_code}")
            return self._build_health(
                status=HealthStatus.UNHEALTHY,
                is_available=False,
                last_error=f"Health probe returned HTTP {response.status_code}",
            )
        except Exception as error:  # noqa: BLE001
            self._record_failure(f"Ollama health probe failed: {error}")
            return self._build_health(
                status=HealthStatus.UNHEALTHY,
                is_available=False,
                last_error=str(error),
            )

    def _messages_to_prompt(self, messages: list[Message]) -> str:
        """Flatten chat messages into an Ollama prompt string."""
        parts: list[str] = []
        for message in messages:
            if message.role == MessageRole.SYSTEM:
                parts.append(f"System: {message.content}")
            elif message.role == MessageRole.USER:
                parts.append(f"User: {message.content}")
            else:
                parts.append(f"Assistant: {message.content}")
        parts.append("Assistant:")
        return "\n\n".join(parts)
