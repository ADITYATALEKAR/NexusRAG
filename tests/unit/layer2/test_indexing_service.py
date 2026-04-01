"""Tests for the Phase 2 indexing service."""

from __future__ import annotations

import uuid

import pytest

from src.layer1_contracts.schemas.chunk import Chunk, ChunkLocation, ChunkMetadata
from src.layer1_contracts.schemas.document import Document, DocumentType
from src.layer1_contracts.schemas.feature_flags import FeatureFlag, FeatureStatus
from src.layer2_domain.compression.quantizer import ScalarQuantizer
from src.layer2_domain.contextual_indexing.context_generator import ContextGenerator
from src.layer2_domain.contextual_indexing.enricher import ChunkContextEnricher
from src.layer2_domain.indexing.service import IndexingService
from src.layer4_providers.embeddings.mock.adapter import MockEmbedder
from src.layer4_providers.stores.metadata.sqlite_adapter import SQLiteMetadataStore
from src.layer4_providers.stores.qdrant.adapter import QdrantAdapter
from src.layer4_providers.stores.sqlite_fts.adapter import SQLiteFTSAdapter
from src.layer8_runtime.feature_flags.manager import FeatureFlagManager


class StubLLMService:
    """Small LLM stub that returns deterministic document context."""

    async def complete(self, request):  # noqa: ANN001
        del request

        class Response:
            content = (
                '{"summary": "VectorCore indexing architecture.", "key_topics": ["indexing", "vectors"]}'
            )

        return Response()


class RecordingEmbedder(MockEmbedder):
    """Embedder that records indexed texts and emits compression-friendly vectors."""

    def __init__(self, dimensions: int = 8) -> None:
        super().__init__(dimensions=dimensions, model="recording-embedder")
        self.calls: list[list[str]] = []

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(list(texts))
        embeddings: list[list[float]] = []
        for index, _text in enumerate(texts):
            base = float(index + 1)
            embeddings.append([base + (dimension / 100.0) for dimension in range(self.dimensions)])
        return embeddings


def build_chunks() -> list[Chunk]:
    """Build a small chunk set for storage tests."""
    return [
        Chunk(
            id="chunk-001",
            document_id="doc-1",
            content="VectorCore keeps retrieval chunks aligned with source offsets.",
            location=ChunkLocation(start_char=0, end_char=61, start_page=1, end_page=1),
            sequence_number=0,
            metadata=ChunkMetadata(section_title="Overview", section_hierarchy=["Overview"], page_numbers=[1]),
        ),
        Chunk(
            id="chunk-002",
            document_id="doc-1",
            content="SQLite FTS provides lexical grounding for exact-match search.",
            location=ChunkLocation(start_char=62, end_char=123, start_page=2, end_page=2),
            sequence_number=1,
            metadata=ChunkMetadata(
                section_title="Storage",
                section_hierarchy=["Overview", "Storage"],
                page_numbers=[2],
            ),
        ),
    ]


@pytest.mark.asyncio
async def test_indexing_service_indexes_chunks_into_all_stores(tmp_path) -> None:
    """Indexing should populate vector, lexical, and metadata stores together."""
    vector_store = QdrantAdapter(
        url="memory://",
        collection=f"chunks_{uuid.uuid4().hex[:8]}",
        dimensions=8,
    )
    lexical_store = SQLiteFTSAdapter(db_path=str(tmp_path / "lexical.db"))
    metadata_store = SQLiteMetadataStore(db_path=str(tmp_path / "metadata.db"))
    service = IndexingService(
        embedder=MockEmbedder(dimensions=8),
        vector_store=vector_store,
        lexical_store=lexical_store,
        metadata_store=metadata_store,
        batch_size=1,
    )

    chunks = build_chunks()
    result = await service.index_chunks(chunks, document_checksum="checksum-1")
    job = service.job_manager.get(result.job_id)

    assert result.status.value == "completed"
    assert result.chunks_indexed == 2
    assert job is not None
    assert job.status.value == "completed"
    assert job.chunk_ids == ["chunk-001", "chunk-002"]
    assert job.started_at is not None
    assert job.completed_at is not None
    assert await vector_store.count() == 2
    assert any(match[0] == "chunk-001" for match in await lexical_store.search("VectorCore", top_k=5))
    assert (await metadata_store.get_chunk("chunk-001"))["section_title"] == "Overview"
    index_state = await metadata_store.get_index_state("doc-1")
    assert index_state is not None
    assert index_state.document_checksum == "checksum-1"
    assert all(chunk.embedding_model == "mock-embed" for chunk in chunks)


@pytest.mark.asyncio
async def test_indexing_service_uses_contextual_and_compressed_runtime_paths(tmp_path) -> None:
    """Feature flags should route live indexing through contextual and compression hooks."""
    vector_store = QdrantAdapter(
        url="memory://",
        collection=f"chunks_{uuid.uuid4().hex[:8]}",
        dimensions=8,
    )
    lexical_store = SQLiteFTSAdapter(db_path=str(tmp_path / "lexical.db"))
    metadata_store = SQLiteMetadataStore(db_path=str(tmp_path / "metadata.db"))
    feature_flags = FeatureFlagManager(
        flags=[
            FeatureFlag(name="contextual_indexing", status=FeatureStatus.ENABLED),
            FeatureFlag(
                name="vector_compression",
                status=FeatureStatus.BENCHMARK_GATED,
                benchmark_threshold=5.0,
            ),
        ]
    )
    embedder = RecordingEmbedder(dimensions=8)
    service = IndexingService(
        embedder=embedder,
        vector_store=vector_store,
        lexical_store=lexical_store,
        metadata_store=metadata_store,
        feature_flags=feature_flags,
        contextual_enricher=ChunkContextEnricher(ContextGenerator(StubLLMService())),
        compression_quantizer=ScalarQuantizer(),
        compression_state_path=str(tmp_path / "vector_compression.npz"),
    )
    document = Document(
        id="document-01",
        content="VectorCore keeps retrieval chunks aligned with source offsets.",
        document_type=DocumentType.MD,
    )

    result = await service.index_chunks(build_chunks(), document_checksum="checksum-ctx", document=document)
    stored_point = (await vector_store.fetch(["chunk-001"]))[0]

    assert result.status.value == "completed"
    assert embedder.calls[0][0].startswith("Document: VectorCore indexing architecture.")
    assert feature_flags.is_enabled("vector_compression") is True
    assert (tmp_path / "vector_compression.npz").exists()
    assert stored_point[2]["contextual"] is True
    assert stored_point[2]["vector_compressed"] is True
