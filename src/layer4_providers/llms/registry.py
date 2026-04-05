"""Helpers for constructing configured LLM providers."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any

from src.layer1_contracts.interfaces.llm import LLMProviderInterface
from src.layer4_providers.llms.anthropic.adapter import AnthropicProvider
from src.layer4_providers.llms.deepseek.adapter import DeepSeekProvider
from src.layer4_providers.llms.google.adapter import GoogleProvider
from src.layer4_providers.llms.groq.adapter import GroqProvider
from src.layer4_providers.llms.mock.provider import MockLLMProvider
from src.layer4_providers.llms.ollama.adapter import OllamaProvider
from src.layer4_providers.llms.openai.adapter import OpenAIProvider
from src.layer4_providers.llms.qwen.adapter import QwenProvider
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
    "deepseek": "DEEPSEEK_API_KEY",
    "qwen": "DASHSCOPE_API_KEY",
}


def load_provider_config(config_dir: Path) -> dict[str, Any]:
    """Load the Phase 4 provider config as a raw mapping."""
    return ConfigLoader(config_dir=config_dir).load_yaml("providers/llm-providers.yaml").get("providers", {})


def build_configured_providers(
    config: dict[str, Any],
    include_uncredentialed: bool = False,
) -> list[LLMProviderInterface]:
    """Build configured real providers in priority order.

    If no providers have credentials, falls back to ``NEXUSRAG_FALLBACK_LLM_KEY``
    env var which is auto-detected to the correct provider.
    """
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

    if not providers:
        fallback_key = os.getenv("NEXUSRAG_FALLBACK_LLM_KEY")
        if fallback_key:
            providers = detect_provider_from_key(fallback_key)

    return providers


def build_provider(
    vendor: str,
    model: str,
    timeout: float,
    base_url: str | None = None,
    api_key: str | None = None,
) -> LLMProviderInterface | None:
    """Build one concrete provider adapter."""
    if vendor == "openai":
        return OpenAIProvider(model=model, timeout=timeout, api_key=api_key)
    if vendor == "anthropic":
        return AnthropicProvider(model=model, timeout=timeout, api_key=api_key)
    if vendor == "google":
        return GoogleProvider(model=model, timeout=timeout, api_key=api_key)
    if vendor == "groq":
        return GroqProvider(model=model, timeout=timeout, api_key=api_key)
    if vendor == "deepseek":
        return DeepSeekProvider(model=model, timeout=timeout, api_key=api_key)
    if vendor == "qwen":
        return QwenProvider(model=model, timeout=timeout, api_key=api_key)
    if vendor == "ollama":
        return OllamaProvider(model=model, timeout=timeout, base_url=base_url or "http://localhost:11434")
    return None


# ── Auto-detect provider from API key pattern ──────────────────────────

_KEY_DETECTION_RULES: list[tuple[str, str, str]] = [
    # (prefix_or_pattern, vendor, default_model)
    ("AIzaSy", "google", "gemini-2.5-flash"),
    ("sk-ant-", "anthropic", "claude-sonnet-4-20250514"),
    ("sk-", "openai", "gpt-4.1-mini"),
    ("gsk_", "groq", "llama-3.3-70b-versatile"),
    ("dsk-", "deepseek", "deepseek-chat"),
    ("dsk_", "deepseek", "deepseek-chat"),
    ("sk-", "deepseek", "deepseek-chat"),
]


def detect_provider_from_key(api_key: str) -> list[LLMProviderInterface]:
    """Auto-detect which provider(s) an API key belongs to and return ready providers.

    Because some prefixes overlap (e.g. ``sk-`` is used by both OpenAI and
    DeepSeek), this returns a list so the failover system can try each one.
    """
    if not api_key:
        return []

    providers: list[LLMProviderInterface] = []
    seen_vendors: set[str] = set()

    # Google keys have a unique prefix
    if api_key.startswith("AIzaSy"):
        providers.append(GoogleProvider(api_key=api_key, model="gemini-2.5-flash"))
        seen_vendors.add("google")

    # Anthropic keys
    if api_key.startswith("sk-ant-"):
        providers.append(AnthropicProvider(api_key=api_key, model="claude-sonnet-4-20250514"))
        seen_vendors.add("anthropic")

    # Groq keys
    if api_key.startswith("gsk_"):
        providers.append(GroqProvider(api_key=api_key, model="llama-3.3-70b-versatile"))
        seen_vendors.add("groq")

    # DashScope / Qwen keys
    if api_key.startswith("sk-") and len(api_key) > 30 and not api_key.startswith("sk-ant-"):
        # Qwen DashScope keys look like sk-<32+ hex chars>
        providers.append(QwenProvider(api_key=api_key, model="qwen-plus"))
        seen_vendors.add("qwen")

    # DeepSeek keys (dsk- prefix or generic sk- that could be DeepSeek)
    if api_key.startswith("dsk-") or api_key.startswith("dsk_"):
        providers.append(DeepSeekProvider(api_key=api_key, model="deepseek-chat"))
        seen_vendors.add("deepseek")

    # OpenAI / generic sk- keys — try OpenAI and DeepSeek
    if api_key.startswith("sk-") and "anthropic" not in seen_vendors:
        if "openai" not in seen_vendors:
            providers.append(OpenAIProvider(api_key=api_key, model="gpt-4.1-mini"))
            seen_vendors.add("openai")
        if "deepseek" not in seen_vendors:
            providers.append(DeepSeekProvider(api_key=api_key, model="deepseek-chat"))
            seen_vendors.add("deepseek")

    # If no prefix matched, try all major providers and let failover sort it out
    if not providers:
        providers.append(OpenAIProvider(api_key=api_key, model="gpt-4.1-mini"))
        providers.append(GoogleProvider(api_key=api_key, model="gemini-2.5-flash"))
        providers.append(AnthropicProvider(api_key=api_key, model="claude-sonnet-4-20250514"))
        providers.append(DeepSeekProvider(api_key=api_key, model="deepseek-chat"))
        providers.append(QwenProvider(api_key=api_key, model="qwen-plus"))

    return providers


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
