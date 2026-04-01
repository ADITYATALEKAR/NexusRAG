"""Tests for the lexical retriever."""

from __future__ import annotations

from datetime import datetime, timezone
import uuid

import pytest

from src.layer1_contracts.schemas.chunk import Chunk, ChunkLocation, ChunkMetadata
from src.layer2_domain.indexing.service import IndexingService
from src.layer2_domain.retrieval.lexical_retriever import LexicalRetriever
from src.layer4_providers.embeddings.mock.adapter import MockEmbedder
from src.layer4_providers.stores.metadata.sqlite_adapter import SQLiteMetadataStore
from src.layer4_providers.stores.qdrant.adapter import QdrantAdapter
from src.layer4_providers.stores.sqlite_fts.adapter import SQLiteFTSAdapter


async def build_lexical_retriever(tmp_path) -> LexicalRetriever:
    embedder = MockEmbedder(dimensions=32)
    vector_store = QdrantAdapter(
        url="memory://",
        collection=f"lex_{uuid.uuid4().hex[:8]}",
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
    chunks = [
        Chunk(
            id="chunk-bm25-hit",
            document_id="doc-1",
            content="BM25 lexical retrieval is excellent for exact hybrid retrieval terminology.",
            location=ChunkLocation(start_char=0, end_char=72),
            sequence_number=0,
            metadata=ChunkMetadata(document_title="Lexical Guide", section_title="BM25", page_numbers=[1]),
            created_at=datetime.now(timezone.utc),
        ),
        Chunk(
            id="chunk-other",
            document_id="doc-2",
            content="Prompt engineering and answer synthesis happen after retrieval.",
            location=ChunkLocation(start_char=0, end_char=60),
            sequence_number=1,
            metadata=ChunkMetadata(document_title="Generation Guide", section_title="Later", page_numbers=[2]),
            created_at=datetime.now(timezone.utc),
        ),
    ]
    await indexing_service.index_chunks(chunks, document_checksum="lexical-checksum")
    return LexicalRetriever(lexical_store=lexical_store, metadata_store=metadata_store)


@pytest.mark.asyncio
async def test_lexical_retriever_returns_bm25_scored_candidates(tmp_path) -> None:
    """Lexical retrieval should return BM25-based results for exact terms."""
    retriever = await build_lexical_retriever(tmp_path)

    candidates, latency_ms = await retriever.retrieve("hybrid retrieval terminology", top_k=2)

    assert latency_ms >= 0
    assert candidates
    assert candidates[0].chunk_id == "chunk-bm25-hit"
    assert candidates[0].scores.lexical_score > 0.0
