"""Unit tests for Phase 6 contextual indexing."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.layer1_contracts.schemas.chunk import Chunk, ChunkLocation, ChunkMetadata
from src.layer1_contracts.schemas.document import Document, DocumentType
from src.layer1_contracts.schemas.feature_flags import FeatureFlag, FeatureStatus
from src.layer2_domain.contextual_indexing.context_generator import ContextGenerator
from src.layer2_domain.contextual_indexing.enricher import ChunkContextEnricher
from src.layer2_domain.contextual_indexing.service import ContextualIndexingService
from src.layer4_providers.embeddings.mock.adapter import MockEmbedder
from src.layer8_runtime.feature_flags.manager import FeatureFlagManager


class StubLLMService:
    """Small LLM stub that returns deterministic JSON payloads."""

    def __init__(self) -> None:
        self.prompts: list[str] = []

    async def complete(self, request) -> SimpleNamespace:
        self.prompts.append(request.messages[-1].content)
        return SimpleNamespace(
            content='{"summary": "Vector search system overview.", "key_topics": ["vector", "retrieval"]}'
        )


class RecordingEmbedder(MockEmbedder):
    """Embedder that records the exact texts sent for embedding."""

    def __init__(self) -> None:
        super().__init__(dimensions=16, model="recording-embedder")
        self.calls: list[list[str]] = []

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(list(texts))
        return await super().embed(texts)


class InMemoryVectorStore:
    """Tiny vector store stub for contextual indexing tests."""

    def __init__(self) -> None:
        self.inserts: list[tuple[list[str], list[list[float]], list[dict] | None]] = []

    async def insert(self, ids, vectors, metadata=None):
        self.inserts.append((list(ids), list(vectors), metadata))
        return len(ids)


def _document() -> Document:
    return Document(
        id="document-01",
        content="Vector search retrieves relevant chunks from enterprise knowledge bases.",
        document_type=DocumentType.MD,
    )


def _chunks() -> list[Chunk]:
    return [
        Chunk(
            id="chunk-0001",
            document_id="document-01",
            content="Dense retrieval finds semantic neighbors.",
            location=ChunkLocation(start_char=0, end_char=39),
            sequence_number=0,
            metadata=ChunkMetadata(
                document_title="Vector Guide",
                section_title="Retrieval",
                section_hierarchy=["Guide", "Retrieval"],
            ),
        )
    ]


@pytest.mark.asyncio
async def test_chunk_context_enricher_prepends_document_context() -> None:
    """Enrichment should prepend summary and section context to chunk text."""
    generator = ContextGenerator(StubLLMService())
    enricher = ChunkContextEnricher(generator, max_context_tokens=20)

    enriched = await enricher.enrich(_chunks(), _document())

    assert enriched[0].contextual_content.startswith("Document: Vector search system overview.")
    assert "Section: Retrieval" in enriched[0].contextual_content
    assert enriched[0].original_content == "Dense retrieval finds semantic neighbors."


@pytest.mark.asyncio
async def test_contextual_indexing_service_uses_original_content_when_disabled() -> None:
    """Disabled flags should keep indexing on the core chunk content path."""
    embedder = RecordingEmbedder()
    vector_store = InMemoryVectorStore()
    feature_flags = FeatureFlagManager(
        flags=[FeatureFlag(name="contextual_indexing", status=FeatureStatus.DISABLED)]
    )
    service = ContextualIndexingService(
        enricher=ChunkContextEnricher(ContextGenerator(StubLLMService())),
        embedder=embedder,
        vector_store=vector_store,
        feature_flags=feature_flags,
    )

    result = await service.index_with_context(_chunks(), _document())

    assert result.status.value == "completed"
    assert embedder.calls[0][0] == "Dense retrieval finds semantic neighbors."
    assert vector_store.inserts[0][2][0]["contextual"] is False


@pytest.mark.asyncio
async def test_contextual_indexing_service_prepends_context_when_enabled() -> None:
    """Enabled contextual indexing should prepend context before embedding."""
    embedder = RecordingEmbedder()
    vector_store = InMemoryVectorStore()
    feature_flags = FeatureFlagManager(
        flags=[FeatureFlag(name="contextual_indexing", status=FeatureStatus.ENABLED)]
    )
    service = ContextualIndexingService(
        enricher=ChunkContextEnricher(ContextGenerator(StubLLMService())),
        embedder=embedder,
        vector_store=vector_store,
        feature_flags=feature_flags,
    )

    result = await service.index_with_context(_chunks(), _document())

    assert result.status.value == "completed"
    assert embedder.calls[0][0].startswith("Document: Vector search system overview.")
    assert vector_store.inserts[0][2][0]["contextual"] is True
