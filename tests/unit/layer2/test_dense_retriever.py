"""Tests for the dense retriever."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import uuid

import pytest

from src.layer1_contracts.schemas.chunk import Chunk, ChunkLocation, ChunkMetadata
from src.layer2_domain.indexing.service import IndexingService
from src.layer2_domain.retrieval.dense_retriever import DenseRetriever
from src.layer4_providers.embeddings.mock.adapter import MockEmbedder
from src.layer4_providers.stores.metadata.sqlite_adapter import SQLiteMetadataStore
from src.layer4_providers.stores.qdrant.adapter import QdrantAdapter
from src.layer4_providers.stores.sqlite_fts.adapter import SQLiteFTSAdapter


async def build_dense_retriever(tmp_path) -> DenseRetriever:
    embedder = MockEmbedder(dimensions=32)
    vector_store = QdrantAdapter(
        url="memory://",
        collection=f"dense_{uuid.uuid4().hex[:8]}",
        dimensions=embedder.dimensions,
    )
    lexical_store = SQLiteFTSAdapter(db_path=str(tmp_path / "lexical.db"))
    metadata_store = SQLiteMetadataStore(db_path=str(tmp_path / "metadata.db"))
    indexing_service = IndexingService(
        embedder=embedder,
        vector_store=vector_store,
        lexical_store=lexical_store,
        metadata_store=metadata_store,
    )
    now = datetime.now(timezone.utc)
    chunks = [
        Chunk(
            id="chunk-old-rel",
            document_id="doc-1",
            content="Hybrid retrieval combines dense vectors and lexical BM25 for diagnostics.",
            location=ChunkLocation(start_char=0, end_char=73),
            sequence_number=0,
            metadata=ChunkMetadata(
                document_title="Retrieval Guide",
                document_type="md",
                tags=["rag", "hybrid"],
                trust_score=0.95,
                section_title="Overview",
                page_numbers=[1],
            ),
            created_at=now - timedelta(days=90),
        ),
        Chunk(
            id="chunk-fresh-partial",
            document_id="doc-2",
            content="Fresh monitoring notes mention retrieval latency and system freshness.",
            location=ChunkLocation(start_char=0, end_char=69),
            sequence_number=1,
            metadata=ChunkMetadata(
                document_title="Operations Notes",
                document_type="md",
                tags=["ops"],
                trust_score=0.9,
                section_title="Notes",
                page_numbers=[2],
            ),
            created_at=now,
        ),
    ]
    await indexing_service.index_chunks(chunks, document_checksum="dense-checksum")
    return DenseRetriever(embedder=embedder, vector_store=vector_store, metadata_store=metadata_store)


@pytest.mark.asyncio
async def test_dense_retriever_returns_cosine_scored_candidates(tmp_path) -> None:
    """Dense retrieval should return raw cosine-style similarity scores for matching chunks."""
    retriever = await build_dense_retriever(tmp_path)

    candidates, latency_ms = await retriever.retrieve("hybrid retrieval diagnostics", top_k=2)

    assert latency_ms >= 0
    assert retriever.last_query_embedding_time_ms >= 0
    assert candidates
    assert candidates[0].chunk_id == "chunk-old-rel"
    assert isinstance(candidates[0].scores.dense_score, float)
