"""Feature-gated contextual indexing service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol

from src.layer1_contracts.interfaces.embedder import EmbedderInterface
from src.layer1_contracts.interfaces.vector_store import VectorStoreInterface
from src.layer1_contracts.schemas.chunk import Chunk
from src.layer1_contracts.schemas.document import Document
from src.layer1_contracts.schemas.indexing import IndexStatus, IndexingResult
from src.layer2_domain.contextual_indexing.enricher import ChunkContextEnricher


class FeatureFlagReader(Protocol):
    """Minimal protocol for feature flag reads from lower layers."""

    def is_enabled(self, name: str) -> bool: ...


class ContextualIndexingService:
    """Index chunks with optional document context prepended before embedding."""

    def __init__(
        self,
        enricher: ChunkContextEnricher,
        embedder: EmbedderInterface,
        vector_store: VectorStoreInterface,
        feature_flags: FeatureFlagReader,
    ) -> None:
        self.enricher = enricher
        self.embedder = embedder
        self.vector_store = vector_store
        self.feature_flags = feature_flags

    async def index_with_context(self, chunks: list[Chunk], document: Document) -> IndexingResult:
        """Index chunks using contextual or standard content based on the feature flag."""
        started = datetime.now(timezone.utc)
        if not chunks:
            return IndexingResult(
                job_id=f"ctx-{document.id}",
                document_id=document.id,
                status=IndexStatus.COMPLETED,
                chunks_indexed=0,
                vector_index_time_ms=0,
                lexical_index_time_ms=0,
                total_time_ms=0,
            )

        if not self.feature_flags.is_enabled("contextual_indexing"):
            return await self._standard_index(chunks, document, started)

        contextual_chunks = await self.enricher.enrich(chunks, document)
        embeddings = await self.embedder.embed([chunk.contextual_content for chunk in contextual_chunks])
        metadata = [
            {
                "document_id": document.id,
                "contextual": True,
                "context_source": chunk.context_source,
                "context_tokens": chunk.context_tokens,
            }
            for chunk in contextual_chunks
        ]
        await self.vector_store.insert([chunk.chunk_id for chunk in contextual_chunks], embeddings, metadata)
        total_time_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
        return IndexingResult(
            job_id=f"ctx-{document.id}",
            document_id=document.id,
            status=IndexStatus.COMPLETED,
            chunks_indexed=len(chunks),
            vector_index_time_ms=total_time_ms,
            lexical_index_time_ms=0,
            total_time_ms=total_time_ms,
        )

    async def _standard_index(
        self,
        chunks: list[Chunk],
        document: Document,
        started: datetime,
    ) -> IndexingResult:
        """Index chunks without contextual augmentation."""
        embeddings = await self.embedder.embed([chunk.content for chunk in chunks])
        metadata = [{"document_id": document.id, "contextual": False} for _ in chunks]
        await self.vector_store.insert([chunk.id for chunk in chunks], embeddings, metadata)
        total_time_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
        return IndexingResult(
            job_id=f"std-{document.id}",
            document_id=document.id,
            status=IndexStatus.COMPLETED,
            chunks_indexed=len(chunks),
            vector_index_time_ms=total_time_ms,
            lexical_index_time_ms=0,
            total_time_ms=total_time_ms,
        )
