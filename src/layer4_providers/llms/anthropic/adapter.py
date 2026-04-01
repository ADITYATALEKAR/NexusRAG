"""Anthropic LLM provider."""

from __future__ import annotations

import json
import os
import time

import httpx

from src.layer0_core.errors import ProviderError, TimeoutError
from src.layer1_contracts.schemas.health import HealthStatus, ProviderHealth
from src.layer1_contracts.schemas.llm import LLMRequest, LLMResponse, LLMUsage, MessageRole
from src.layer4_providers.llms.base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """Anthropic messages API provider."""

    def __init__(
        self,
        provider_id: str = "anthropic",
        api_key: str | None = None,
        model: str = "claude-sonnet-4-20250514",
        timeout: float = 60.0,
    ) -> None:
        super().__init__(
            provider_id=provider_id,
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            base_url="https://api.anthropic.com/v1",
            model=model,
            timeout=timeout,
        )

    @property
    def vendor(self) -> str:
        """Return provider vendor."""
        return "anthropic"

    def supports_model(self, model: str) -> bool:
        """Return whether Anthropic can serve the requested model."""
        return "claude" in model.lower()

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Execute a messages request against Anthropic."""
        self._ensure_api_key()
        self.total_requests += 1
        started_at = time.perf_counter()
        system_prompt: str | None = None
        messages: list[dict[str, str]] = []
        for message in request.messages:
            if message.role == MessageRole.SYSTEM:
                system_prompt = message.content
                continue
            messages.append({"role": message.role.value, "content": message.content})
        payload: dict[str, object] = {
            "model": self._resolve_model(request.config.model),
            "messages": messages,
            "max_tokens": request.config.max_tokens,
            "temperature": request.config.temperature,
        }
        if system_prompt:
            payload["system"] = system_prompt
        try:
            response = await self._client.post(
                f"{self._base_url}/messages",
                json=payload,
                headers={
                    "x-api-key": str(self._api_key),
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                timeout=request.timeout_seconds,
            )
            response_body = response.json()
            if response.status_code != 200:
                self._record_failure(f"Anthropic HTTP {response.status_code}")
                self._handle_error(response.status_code, response_body, "Anthropic")
            latency_ms = int((time.perf_counter() - started_at) * 1000)
            self._record_success(latency_ms)
            usage = response_body.get("usage", {})
            content_blocks = response_body.get("content", [])
            text = ""
            for block in content_blocks:
                if block.get("type") == "text":
                    text += str(block.get("text", ""))
            return LLMResponse(
                request_id=request.id,
                content=text,
                provider=self.provider_id,
                model=response_body.get("model", self._resolve_model(request.config.model)),
                usage=LLMUsage(
                    prompt_tokens=int(usage.get("input_tokens", 0)),
                    completion_tokens=int(usage.get("output_tokens", 0)),
                    total_tokens=int(usage.get("input_tokens", 0)) + int(usage.get("output_tokens", 0)),
                ),
                latency_ms=latency_ms,
                finish_reason=str(response_body.get("stop_reason", "stop")),
            )
        except httpx.TimeoutException as error:
            self._record_failure("Anthropic request timed out")
            raise TimeoutError(
                "Anthropic request timed out",
                timeout_seconds=request.timeout_seconds,
                cause=error,
            ) from error
        except httpx.HTTPError as error:
            self._record_failure("Anthropic request failed")
            raise ProviderError(
                "Anthropic request failed",
                provider_id=self.provider_id,
                cause=error,
            ) from error

    async def complete_stream(self, request: LLMRequest):
        """Stream text deltas from Anthropic's messages API."""
        self._ensure_api_key()
        system_prompt: str | None = None
        messages: list[dict[str, str]] = []
        for message in request.messages:
            if message.role == MessageRole.SYSTEM:
                system_prompt = message.content
                continue
            messages.append({"role": message.role.value, "content": message.content})
        payload: dict[str, object] = {
            "model": self._resolve_model(request.config.model),
            "messages": messages,
            "max_tokens": request.config.max_tokens,
            "temperature": request.config.temperature,
            "stream": True,
        }
        if system_prompt:
            payload["system"] = system_prompt
        async with self._client.stream(
            "POST",
            f"{self._base_url}/messages",
            json=payload,
            headers={
                "x-api-key": str(self._api_key),
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            timeout=request.timeout_seconds,
        ) as response:
            if response.status_code != 200:
                body = await response.aread()
                self._record_failure(f"Anthropic HTTP {response.status_code}")
                self._handle_error(
                    response.status_code,
                    {"error": body.decode("utf-8", errors="ignore")},
                    "Anthropic",
                )
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                raw = line[6:]
                if not raw or raw == "[DONE]":
                    continue
                data = json.loads(raw)
                if data.get("type") != "content_block_delta":
                    continue
                delta = data.get("delta", {})
                if delta.get("type") == "text_delta" and "text" in delta:
                    yield str(delta["text"])

    async def health_check(self) -> ProviderHealth:
        """Return provider availability based on configured credentials."""
        if not self.api_key_configured:
            return self._build_health(
                status=HealthStatus.UNHEALTHY,
                is_available=False,
                last_error="API key not configured",
            )
        return self._build_health(status=HealthStatus.HEALTHY, is_available=True)
