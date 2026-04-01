"""Late chunking helpers for document-aware embeddings."""

from __future__ import annotations

import math

from src.layer1_contracts.interfaces.embedder import EmbedderInterface
from src.layer1_contracts.schemas.chunk import Chunk
from src.layer1_contracts.schemas.document import Document


class LateChunker:
    """Blend full-document and per-chunk embeddings to preserve global context."""

    def __init__(self, embedder: EmbedderInterface, doc_weight: float = 0.2) -> None:
        self.embedder = embedder
        self.doc_weight = doc_weight

    async def embed_and_chunk(self, document: Document, chunks: list[Chunk]) -> list[tuple[str, list[float]]]:
        """Return normalized blended embeddings for each chunk."""
        doc_embedding = await self.embedder.embed_query(document.content[:32000])
        results: list[tuple[str, list[float]]] = []
        for chunk in chunks:
            chunk_embedding = await self.embedder.embed_query(chunk.content)
            combined = [
                self.doc_weight * doc_value + (1.0 - self.doc_weight) * chunk_value
                for doc_value, chunk_value in zip(doc_embedding, chunk_embedding)
            ]
            norm = math.sqrt(sum(value * value for value in combined))
            if norm > 0:
                combined = [value / norm for value in combined]
            results.append((chunk.id, combined))
        return results
