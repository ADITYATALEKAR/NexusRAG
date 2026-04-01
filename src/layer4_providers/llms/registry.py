"""Helpers for constructing configured LLM providers."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any

from src.layer1_contracts.interfaces.llm import LLMProviderInterface
from src.layer4_providers.llms.anthropic.adapter import AnthropicProvider
from src.layer4_providers.llms.google.adapter import GoogleProvider
from src.layer4_providers.llms.groq.adapter import GroqProvider
from src.layer4_providers.llms.mock.provider import MockLLMProvider
from src.layer4_providers.llms.ollama.adapter import OllamaProvider
from src.layer4_providers.llms.openai.adapter import OpenAIProvider
from src.layer8_runtime.config.loader import ConfigLoader


def build_mock_provider(provider_id: str, vendor: str, model: str) -> MockLLMProvider:
    """Create a default mock provider for a configured provider slot."""
    return MockLLMProvider(provider_id=provider_id, vendor=vendor, model=model)


@dataclass(frozen=True)
class ProviderDefinition:
    """Normalized provider definition loaded from config."""

    vendor: str
    enabled: bool
    priority: int
    models: list[str]
    timeout: float
    base_url: str | None = None


_CREDENTIAL_ENV = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
    "groq": "GROQ_API_KEY",
}


def load_provider_config(config_dir: Path) -> dict[str, Any]:
    """Load the Phase 4 provider config as a raw mapping."""
    return ConfigLoader(config_dir=config_dir).load_yaml("providers/llm-providers.yaml").get("providers", {})


def build_configured_providers(
    config: dict[str, Any],
    include_uncredentialed: bool = False,
) -> list[LLMProviderInterface]:
    """Build configured real providers in priority order."""
    definitions = _normalize_provider_definitions(config)
    providers: list[LLMProviderInterface] = []
    for definition in definitions:
        if not definition.enabled or not definition.models:
            continue
        if not include_uncredentialed and not _has_credentials(definition.vendor):
            continue
        provider = build_provider(
            vendor=definition.vendor,
            model=definition.models[0],
            timeout=definition.timeout,
            base_url=definition.base_url,
        )
        if provider is not None:
            providers.append(provider)
    return providers


def build_provider(
    vendor: str,
    model: str,
    timeout: float,
    base_url: str | None = None,
) -> LLMProviderInterface | None:
    """Build one concrete provider adapter."""
    if vendor == "openai":
        return OpenAIProvider(model=model, timeout=timeout)
    if vendor == "anthropic":
        return AnthropicProvider(model=model, timeout=timeout)
    if vendor == "google":
        return GoogleProvider(model=model, timeout=timeout)
    if vendor == "groq":
        return GroqProvider(model=model, timeout=timeout)
    if vendor == "ollama":
        return OllamaProvider(model=model, timeout=timeout, base_url=base_url or "http://localhost:11434")
    return None


def _normalize_provider_definitions(config: dict[str, Any]) -> list[ProviderDefinition]:
    """Normalize raw YAML config into typed provider definitions."""
    definitions: list[ProviderDefinition] = []
    for vendor, raw in config.items():
        if not isinstance(raw, dict):
            continue
        definitions.append(
            ProviderDefinition(
                vendor=vendor,
                enabled=bool(raw.get("enabled", False)),
                priority=int(raw.get("priority", 100)),
                models=[str(model) for model in raw.get("models", [])],
                timeout=float(raw.get("timeout", 60)),
                base_url=str(raw["base_url"]) if raw.get("base_url") else None,
            )
        )
    return sorted(definitions, key=lambda definition: definition.priority)


def _has_credentials(vendor: str) -> bool:
    """Return whether the required credentials for a vendor exist."""
    if vendor == "ollama":
        return True
    env_name = _CREDENTIAL_ENV.get(vendor)
    if env_name is None:
        return False
    return bool(os.getenv(env_name))
