"""Overlap handling for generated chunks."""

from __future__ import annotations

from src.layer1_contracts.schemas.chunk import Chunk


class OverlapHandler:
    """Add adjacent overlap context to chunks."""

    def apply(self, chunks: list[Chunk], overlap: int) -> list[Chunk]:
        """Prefix chunks with trailing context from their previous neighbor."""
        if overlap <= 0:
            return chunks

        for index, chunk in enumerate(chunks):
            if index == 0:
                continue
            previous_content = chunks[index - 1].content
            prefix = previous_content[-overlap:] if len(previous_content) > overlap else previous_content
            chunk.content = f"...{prefix}\n\n{chunk.content}"
            chunk.token_count = len(chunk.content.split())
        return chunks
