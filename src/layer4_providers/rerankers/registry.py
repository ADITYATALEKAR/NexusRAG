"""Reranker registry helpers."""

from __future__ import annotations

from src.layer1_contracts.interfaces.reranker import RerankerInterface
from src.layer4_providers.rerankers.mock.adapter import MockReranker


class RerankerRegistry:
    """Simple registry for reranker providers."""

    def __init__(self) -> None:
        self._providers: dict[str, RerankerInterface] = {}

    def register(self, name: str, provider: RerankerInterface) -> None:
        """Register a reranker instance."""
        self._providers[name] = provider

    def get(self, name: str) -> RerankerInterface | None:
        """Return a registered reranker by name."""
        return self._providers.get(name)


def build_reranker(provider: str = "mock", model: str = "mock-reranker") -> RerankerInterface:
    """Build a reranker for the configured provider name."""
    if provider == "mock":
        return MockReranker(model=model)
    raise ValueError(f"Unsupported reranker provider: {provider}")
