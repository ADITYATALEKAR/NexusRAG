"""Google Gemini provider."""

from __future__ import annotations

import json
import os
import time

import httpx

from src.layer0_core.errors import ProviderError, TimeoutError
from src.layer1_contracts.schemas.health import HealthStatus, ProviderHealth
from src.layer1_contracts.schemas.llm import LLMRequest, LLMResponse, LLMUsage, MessageRole
from src.layer4_providers.llms.base import BaseLLMProvider


class GoogleProvider(BaseLLMProvider):
    """Google Generative Language API provider."""

    def __init__(
        self,
        provider_id: str = "google",
        api_key: str | None = None,
        model: str = "gemini-1.5-pro",
        timeout: float = 60.0,
    ) -> None:
        super().__init__(
            provider_id=provider_id,
            api_key=api_key or os.getenv("GOOGLE_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta",
            model=model,
            timeout=timeout,
        )

    @property
    def vendor(self) -> str:
        """Return provider vendor."""
        return "google"

    def supports_model(self, model: str) -> bool:
        """Return whether Google can serve the requested model."""
        return "gemini" in model.lower()

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Execute a completion against Gemini."""
        self._ensure_api_key()
        self.total_requests += 1
        started_at = time.perf_counter()
        system_prompt: str | None = None
        contents: list[dict[str, object]] = []
        for message in request.messages:
            if message.role == MessageRole.SYSTEM:
                system_prompt = message.content
                continue
            role = "user" if message.role == MessageRole.USER else "model"
            contents.append({"role": role, "parts": [{"text": message.content}]})
        payload: dict[str, object] = {
            "contents": contents,
            "generationConfig": {
                "temperature": request.config.temperature,
                "maxOutputTokens": request.config.max_tokens,
                "topP": request.config.top_p,
            },
        }
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        model = self._resolve_model(request.config.model)
        try:
            response = await self._client.post(
                f"{self._base_url}/models/{model}:generateContent",
                params={"key": self._api_key},
                json=payload,
                timeout=request.timeout_seconds,
            )
            response_body = response.json()
            if response.status_code != 200:
                self._record_failure(f"Google HTTP {response.status_code}")
                self._handle_error(response.status_code, response_body, "Google")
            latency_ms = int((time.perf_counter() - started_at) * 1000)
            self._record_success(latency_ms)
            candidate = response_body.get("candidates", [{}])[0]
            content = candidate.get("content", {})
            text = "".join(str(part.get("text", "")) for part in content.get("parts", []))
            usage = response_body.get("usageMetadata", {})
            prompt_tokens = int(usage.get("promptTokenCount", 0))
            completion_tokens = int(usage.get("candidatesTokenCount", 0))
            return LLMResponse(
                request_id=request.id,
                content=text,
                provider=self.provider_id,
                model=model,
                usage=LLMUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                ),
                latency_ms=latency_ms,
                finish_reason=str(candidate.get("finishReason", "stop")).lower(),
            )
        except httpx.TimeoutException as error:
            self._record_failure("Google request timed out")
            raise TimeoutError(
                "Google request timed out",
                timeout_seconds=request.timeout_seconds,
                cause=error,
            ) from error
        except httpx.HTTPError as error:
            self._record_failure("Google request failed")
            raise ProviderError(
                "Google request failed",
                provider_id=self.provider_id,
                cause=error,
            ) from error

    async def complete_stream(self, request: LLMRequest):
        """Stream Gemini text deltas using the SSE endpoint."""
        self._ensure_api_key()
        system_prompt: str | None = None
        contents: list[dict[str, object]] = []
        for message in request.messages:
            if message.role == MessageRole.SYSTEM:
                system_prompt = message.content
                continue
            role = "user" if message.role == MessageRole.USER else "model"
            contents.append({"role": role, "parts": [{"text": message.content}]})
        payload: dict[str, object] = {
            "contents": contents,
            "generationConfig": {
                "temperature": request.config.temperature,
                "maxOutputTokens": request.config.max_tokens,
                "topP": request.config.top_p,
            },
        }
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        model = self._resolve_model(request.config.model)
        async with self._client.stream(
            "POST",
            f"{self._base_url}/models/{model}:streamGenerateContent",
            params={"key": self._api_key, "alt": "sse"},
            json=payload,
            timeout=request.timeout_seconds,
        ) as response:
            if response.status_code != 200:
                body = await response.aread()
                self._record_failure(f"Google HTTP {response.status_code}")
                self._handle_error(
                    response.status_code,
                    {"error": body.decode("utf-8", errors="ignore")},
                    "Google",
                )
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                raw = line[6:]
                if not raw:
                    continue
                data = json.loads(raw)
                for candidate in data.get("candidates", []):
                    content = candidate.get("content", {})
                    for part in content.get("parts", []):
                        if "text" in part:
                            yield str(part["text"])

    async def health_check(self) -> ProviderHealth:
        """Probe the Gemini model endpoint for health."""
        if not self.api_key_configured:
            return self._build_health(
                status=HealthStatus.UNHEALTHY,
                is_available=False,
                last_error="API key not configured",
            )
        try:
            response = await self._client.get(
                f"{self._base_url}/models",
                params={"key": self._api_key},
            )
            if response.status_code == 200:
                return self._build_health(status=HealthStatus.HEALTHY, is_available=True)
            self._record_failure(f"Google health probe returned {response.status_code}")
            return self._build_health(
                status=HealthStatus.UNHEALTHY,
                is_available=False,
                last_error=f"Health probe returned HTTP {response.status_code}",
            )
        except Exception as error:  # noqa: BLE001
            self._record_failure(f"Google health probe failed: {error}")
            return self._build_health(
                status=HealthStatus.UNHEALTHY,
                is_available=False,
                last_error=str(error),
            )
