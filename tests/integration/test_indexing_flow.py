"""Integration tests for the Phase 2 indexing flow."""

from __future__ import annotations

import uuid

import pytest

from src.layer1_contracts.schemas.chunking import ChunkingConfig, ChunkingStrategy
from src.layer1_contracts.schemas.document import DocumentMetadata
from src.layer1_contracts.schemas.normalization import ChunkPrecursor, NormalizedDocument, NormalizedSection
from src.layer2_domain.chunking.service import ChunkingService
from src.layer2_domain.indexing.freshness import FreshnessTracker
from src.layer2_domain.indexing.service import IndexingService
from src.layer3_flows.indexing_flow.flow import IndexingFlow
from src.layer4_providers.embeddings.mock.adapter import MockEmbedder
from src.layer4_providers.stores.metadata.sqlite_adapter import SQLiteMetadataStore
from src.layer4_providers.stores.qdrant.adapter import QdrantAdapter
from src.layer4_providers.stores.sqlite_fts.adapter import SQLiteFTSAdapter


def build_normalized_doc() -> tuple[NormalizedDocument, list[ChunkPrecursor]]:
    """Build a normalized document and chunk precursors for indexing integration tests."""
    section_a = "NexusRAG turns normalized documents into retrieval-ready chunks. " * 4
    section_b = "Freshness tracking prevents unnecessary reindex work. " * 4
    content = f"{section_a}\n\n{section_b}"
    split_point = len(section_a)
    normalized_doc = NormalizedDocument(
        id="norm-doc-1",
        original_document_id="doc-1",
        content=content,
        sections=[
            NormalizedSection(
                id="section-0",
                title="Chunking",
                level=1,
                content=section_a,
                start_char=0,
                end_char=len(section_a),
                page_numbers=[1],
            ),
            NormalizedSection(
                id="section-1",
                title="Freshness",
                level=1,
                content=section_b,
                start_char=split_point + 2,
                end_char=split_point + 2 + len(section_b),
                page_numbers=[2],
            ),
        ],
        metadata=DocumentMetadata(page_count=2, word_count=len(content.split()), char_count=len(content)),
        page_count=2,
        word_count=len(content.split()),
        char_count=len(content),
    )
    precursors = [
        ChunkPrecursor(
            id="pre-0",
            document_id=normalized_doc.id,
            content=section_a,
            section_id="section-0",
            section_title="Chunking",
            section_hierarchy=["Chunking"],
            start_char=0,
            end_char=len(section_a),
            page_numbers=[1],
            suggested_split_points=[110],
        ),
        ChunkPrecursor(
            id="pre-1",
            document_id=normalized_doc.id,
            content=section_b,
            section_id="section-1",
            section_title="Freshness",
            section_hierarchy=["Freshness"],
            start_char=split_point + 2,
            end_char=split_point + 2 + len(section_b),
            page_numbers=[2],
            suggested_split_points=[100],
        ),
    ]
    return normalized_doc, precursors


def build_flow(tmp_path) -> IndexingFlow:
    """Build a fully wired indexing flow with local adapters."""
    chunking_service = ChunkingService(
        default_config=ChunkingConfig(
            strategy=ChunkingStrategy.SEMANTIC,
            target_size=140,
            min_size=40,
            max_size=180,
            overlap=24,
        )
    )
    indexing_service = IndexingService(
        embedder=MockEmbedder(dimensions=8),
        vector_store=QdrantAdapter(
            url="memory://",
            collection=f"chunks_{uuid.uuid4().hex[:8]}",
            dimensions=8,
        ),
        lexical_store=SQLiteFTSAdapter(db_path=str(tmp_path / "lexical.db")),
        metadata_store=SQLiteMetadataStore(db_path=str(tmp_path / "metadata.db")),
    )
    freshness_tracker = FreshnessTracker(indexing_service.metadata_store)
    return IndexingFlow(chunking_service, indexing_service, freshness_tracker)


@pytest.mark.asyncio
async def test_indexing_flow_end_to_end(tmp_path) -> None:
    """Normalized documents should chunk and index end to end."""
    normalized_doc, chunk_precursors = build_normalized_doc()
    flow = build_flow(tmp_path)

    result = await flow.execute(normalized_doc, chunk_precursors, document_checksum="checksum-1")
    job = flow.indexing_service.job_manager.get(result.job_id)

    assert result.status.value == "completed"
    assert job is not None
    assert job.status.value == "completed"
    assert result.chunks_indexed > 0
    assert await flow.indexing_service.vector_store.count() > 0
    assert await flow.indexing_service.lexical_store.search("NexusRAG", top_k=5)
    assert await flow.freshness_tracker.needs_reindex("doc-1", "checksum-1") is False


@pytest.mark.asyncio
async def test_indexing_flow_skips_when_document_is_fresh(tmp_path) -> None:
    """Fresh documents should skip redundant indexing work."""
    normalized_doc, chunk_precursors = build_normalized_doc()
    flow = build_flow(tmp_path)

    first = await flow.execute(normalized_doc, chunk_precursors, document_checksum="checksum-1")
    second = await flow.execute(normalized_doc, chunk_precursors, document_checksum="checksum-1")

    assert first.status.value == "completed"
    assert second.job_id == "skip"
    assert second.chunks_indexed == 0
    assert len(flow.indexing_service.job_manager.list_jobs()) == 1
