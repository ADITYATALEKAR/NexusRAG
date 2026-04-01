"""Mock embedder implementation."""

from __future__ import annotations

import hashlib
import math
import re

from src.layer1_contracts.interfaces.embedder import EmbedderInterface


class MockEmbedder(EmbedderInterface):
    """Deterministic mock embedder for Phase 2 indexing tests."""

    def __init__(self, dimensions: int = 384, model: str = "mock-embed") -> None:
        self._dimensions = dimensions
        self._model = model

    @property
    def model(self) -> str:
        """Return the embedder model name."""
        return self._model

    @property
    def dimensions(self) -> int:
        """Return embedding dimensions."""
        return self._dimensions

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate deterministic mock embeddings for multiple texts."""
        return [self._text_to_vector(text) for text in texts]

    async def embed_query(self, query: str) -> list[float]:
        """Generate a deterministic embedding for one query."""
        return self._text_to_vector(query)

    async def health_check(self) -> bool:
        """Return provider health."""
        return True

    def _text_to_vector(self, text: str) -> list[float]:
        """Generate a deterministic overlap-sensitive vector."""
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        if not tokens:
            tokens = [text.lower()]

        vector = [0.0] * self._dimensions
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for index in range(self._dimensions):
                byte = digest[index % len(digest)]
                vector[index] += (byte / 255.0) * 2.0 - 1.0

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]
