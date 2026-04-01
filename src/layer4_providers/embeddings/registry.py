"""Embedding provider registry helpers."""

from src.layer1_contracts.interfaces.embedder import EmbedderInterface
from src.layer4_providers.embeddings.mock.adapter import MockEmbedder


def build_default_embedders() -> dict[str, EmbedderInterface]:
    """Build the default embedding provider registry for Phase 2."""
    return {"mock": MockEmbedder()}
