"""Shared base utilities for real LLM providers."""

from __future__ import annotations

from collections.abc import AsyncIterator
import json
import time
from typing import Any

import httpx

from src.layer0_core.errors import ProviderError, RateLimitError, TimeoutError
from src.layer1_contracts.interfaces.llm import LLMProviderInterface
from src.layer1_contracts.schemas.health import HealthStatus, ProviderHealth
from src.layer1_contracts.schemas.llm import LLMRequest, LLMResponse, LLMUsage
from src.layer6_security.secrets.masking import SecretMasker


class BaseLLMProvider(LLMProviderInterface):
    """Base class with shared HTTP, stats, and error handling."""

    def __init__(
        self,
        provider_id: str,
        api_key: str | None,
        base_url: str,
        model: str,
        timeout: float = 60.0,
    ) -> None:
        self._provider_id = provider_id
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)
        self._masker = SecretMasker()
        self._last_error: str | None = None
        self._total_latency_ms = 0
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0

    @property
    def provider_id(self) -> str:
        """Return provider identifier."""
        return self._provider_id

    @property
    def model(self) -> str:
        """Return default model name."""
        return self._model

    @property
    def api_key_configured(self) -> bool:
        """Return whether credentials are configured for the provider."""
        return bool(self._api_key)

    def supports_model(self, model: str) -> bool:
        """Return whether the provider can serve a requested model."""
        return True

    def _resolve_model(self, requested_model: str | None) -> str:
        """Resolve a model override while preserving cross-vendor failover."""
        if requested_model and self.supports_model(requested_model):
            return requested_model
        return self._model

    def _ensure_api_key(self) -> None:
        """Raise when a provider requiring credentials is not configured."""
        if not self.api_key_configured:
            raise ProviderError(
                f"{self.vendor} API key not configured",
                provider_id=self._provider_id,
            )

    def _record_success(self, latency_ms: int) -> None:
        """Update statistics for a successful call."""
        self.successful_requests += 1
        self._last_error = None
        self._total_latency_ms += latency_ms

    def _record_failure(self, message: str) -> None:
        """Update statistics for a failed call."""
        self.failed_requests += 1
        self._last_error = self._masker.mask(message)

    def _average_latency(self) -> float | None:
        """Return average latency across successful requests."""
        if self.successful_requests == 0:
            return None
        return self._total_latency_ms / self.successful_requests

    def _build_health(
        self,
        status: HealthStatus,
        is_available: bool,
        last_error: str | None = None,
    ) -> ProviderHealth:
        """Build a typed provider health payload."""
        return ProviderHealth(
            provider_id=self._provider_id,
            provider_type="llm",
            vendor=self.vendor,
            status=status,
            is_available=is_available,
            total_requests=self.total_requests,
            successful_requests=self.successful_requests,
            failed_requests=self.failed_requests,
            avg_latency_ms=self._average_latency(),
            last_error=self._masker.mask(last_error) if last_error else self._last_error,
        )

    def _extract_error_message(self, response_body: Any) -> str:
        """Extract a safe error message from a provider response body."""
        if isinstance(response_body, dict):
            error = response_body.get("error")
            if isinstance(error, dict):
                message = error.get("message") or error.get("type") or json.dumps(error)
            elif error is not None:
                message = str(error)
            else:
                message = response_body.get("message") or json.dumps(response_body)
            return self._masker.mask(message)
        return self._masker.mask(str(response_body))

    def _handle_error(self, status_code: int, response_body: Any, provider: str) -> None:
        """Convert provider HTTP errors into typed domain errors."""
        if status_code == 429:
            retry_after = 60.0
            if isinstance(response_body, dict):
                raw_retry_after = response_body.get("retry_after")
                if raw_retry_after is not None:
                    try:
                        retry_after = float(raw_retry_after)
                    except (TypeError, ValueError):
                        retry_after = 60.0
            raise RateLimitError(f"{provider} rate limited", retry_after=retry_after)
        if status_code == 401:
            raise ProviderError(f"{provider} authentication failed", provider_id=self._provider_id)
        if status_code >= 500:
            raise ProviderError(
                f"{provider} server error: {status_code}",
                provider_id=self._provider_id,
            )
        raise ProviderError(
            f"{provider} error {status_code}: {self._extract_error_message(response_body)}",
            provider_id=self._provider_id,
        )

    async def complete_stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Fallback streaming implementation that yields the full response once."""
        response = await self.complete(request)
        yield response.content

    async def health_check(self) -> ProviderHealth:
        """Return generic provider health when no richer probe is implemented."""
        if not self.api_key_configured:
            return self._build_health(
                status=HealthStatus.UNHEALTHY,
                is_available=False,
                last_error="API key not configured",
            )
        return self._build_health(status=HealthStatus.HEALTHY, is_available=True)

    async def _openai_compatible_complete(
        self,
        request: LLMRequest,
        provider_name: str,
        headers: dict[str, str],
    ) -> LLMResponse:
        """Execute a completion against an OpenAI-compatible chat endpoint."""
        self._ensure_api_key()
        self.total_requests += 1
        started_at = time.perf_counter()
        payload: dict[str, Any] = {
            "model": self._resolve_model(request.config.model),
            "messages": [{"role": message.role.value, "content": message.content} for message in request.messages],
            "temperature": request.config.temperature,
            "max_tokens": request.config.max_tokens,
            "top_p": request.config.top_p,
        }
        if request.config.stop_sequences:
            payload["stop"] = request.config.stop_sequences

        try:
            response = await self._client.post(
                f"{self._base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=request.timeout_seconds,
            )
            response_body = response.json()
            if response.status_code != 200:
                self._record_failure(f"{provider_name} HTTP {response.status_code}")
                self._handle_error(response.status_code, response_body, provider_name)
            latency_ms = int((time.perf_counter() - started_at) * 1000)
            self._record_success(latency_ms)
            usage = response_body.get("usage", {})
            completion = response_body["choices"][0]["message"]["content"]
            return LLMResponse(
                request_id=request.id,
                content=completion,
                provider=self._provider_id,
                model=response_body.get("model", self._resolve_model(request.config.model)),
                usage=LLMUsage(
                    prompt_tokens=int(usage.get("prompt_tokens", 0)),
                    completion_tokens=int(usage.get("completion_tokens", 0)),
                    total_tokens=int(usage.get("total_tokens", 0)),
                ),
                latency_ms=latency_ms,
                finish_reason=str(response_body["choices"][0].get("finish_reason", "stop")),
            )
        except httpx.TimeoutException as error:
            self._record_failure(f"{provider_name} request timed out")
            raise TimeoutError(
                f"{provider_name} request timed out",
                timeout_seconds=request.timeout_seconds,
                cause=error,
            ) from error
        except httpx.HTTPError as error:
            self._record_failure(f"{provider_name} request failed")
            raise ProviderError(
                f"{provider_name} request failed",
                provider_id=self._provider_id,
                cause=error,
            ) from error

    async def _openai_compatible_stream(
        self,
        request: LLMRequest,
        headers: dict[str, str],
    ) -> AsyncIterator[str]:
        """Stream from an OpenAI-compatible chat endpoint."""
        self._ensure_api_key()
        payload: dict[str, Any] = {
            "model": self._resolve_model(request.config.model),
            "messages": [{"role": message.role.value, "content": message.content} for message in request.messages],
            "temperature": request.config.temperature,
            "max_tokens": request.config.max_tokens,
            "stream": True,
        }
        async with self._client.stream(
            "POST",
            f"{self._base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=request.timeout_seconds,
        ) as response:
            if response.status_code != 200:
                body = await response.aread()
                self._record_failure(f"HTTP {response.status_code}")
                self._handle_error(response.status_code, {"error": body.decode('utf-8', errors='ignore')}, self.vendor)
            async for line in response.aiter_lines():
                if not line.startswith("data: ") or line == "data: [DONE]":
                    continue
                data = json.loads(line[6:])
                delta = data["choices"][0].get("delta", {})
                if "content" in delta:
                    yield str(delta["content"])
