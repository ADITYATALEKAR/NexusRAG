"""Chunk enrichment for contextual indexing."""

from __future__ import annotations

from src.layer1_contracts.schemas.chunk import Chunk
from src.layer1_contracts.schemas.contextual import ContextualChunk
from src.layer1_contracts.schemas.document import Document
from src.layer2_domain.contextual_indexing.context_generator import ContextGenerator


class ChunkContextEnricher:
    """Prepend compact document context to chunks before embedding."""

    def __init__(
        self,
        context_generator: ContextGenerator,
        max_context_tokens: int = 100,
        include_document_summary: bool = True,
        include_section_hierarchy: bool = True,
    ) -> None:
        self.context_generator = context_generator
        self.max_context_tokens = max_context_tokens
        self.include_document_summary = include_document_summary
        self.include_section_hierarchy = include_section_hierarchy

    async def enrich(self, chunks: list[Chunk], document: Document) -> list[ContextualChunk]:
        """Return contextualized chunks for the supplied document."""
        doc_ctx = await self.context_generator.generate_document_context(document)
        enriched: list[ContextualChunk] = []
        for chunk in chunks:
            context = self.context_generator.generate_chunk_context(chunk, doc_ctx)
            if not self.include_document_summary and context.startswith("Document:"):
                context = " | ".join(part for part in context.split(" | ") if not part.startswith("Document:"))
            if not self.include_section_hierarchy:
                context = " | ".join(part for part in context.split(" | ") if not part.startswith("Hierarchy:"))
            context = self._trim_tokens(context)
            contextual_content = f"{context}\n\n{chunk.content}" if context else chunk.content
            enriched.append(
                ContextualChunk(
                    chunk_id=chunk.id,
                    original_content=chunk.content,
                    contextual_content=contextual_content,
                    context_source="document_summary",
                    context_tokens=len(context.split()) if context else 0,
                )
            )
        return enriched

    def _trim_tokens(self, context: str) -> str:
        """Trim context to the configured token budget using whitespace tokens."""
        tokens = context.split()
        if len(tokens) <= self.max_context_tokens:
            return context
        return " ".join(tokens[: self.max_context_tokens])
