"""Provider-related enums."""

from enum import Enum


class ProviderType(str, Enum):
    """Supported provider categories."""

    LLM = "llm"
    EMBEDDING = "embedding"
    RERANKER = "reranker"
    VECTOR_STORE = "vector_store"
    LEXICAL_STORE = "lexical_store"
    PARSER = "parser"
    CACHE = "cache"


class ProviderVendor(str, Enum):
    """Supported provider vendors."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    MOCK = "mock"


class ProviderStatus(str, Enum):
    """Provider health lifecycle."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    COOLING_DOWN = "cooling_down"
    DISABLED = "disabled"
