"""Tests for reranking."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import uuid

import pytest

from tests.benchmarks.retrieval_benchmark import RetrievalBenchmark
from src.layer1_contracts.schemas.chunk import Chunk, ChunkLocation, ChunkMetadata
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.retrieval import RetrievalCandidate, RetrievalScores, RetrievalSource
from src.layer1_contracts.schemas.retrieval_config import RetrievalConfig
from src.layer2_domain.indexing.service import IndexingService
from src.layer2_domain.reranking.service import RerankingService
from src.layer2_domain.retrieval.dense_retriever import DenseRetriever
from src.layer2_domain.retrieval.diagnostics import RetrievalDiagnosticsStore
from src.layer2_domain.retrieval.deduplication import CandidateDeduplicator
from src.layer2_domain.retrieval.filters.freshness_filter import FreshnessBooster
from src.layer2_domain.retrieval.filters.metadata_filter import MetadataFilter
from src.layer2_domain.retrieval.filters.trust_filter import TrustFilter
from src.layer2_domain.retrieval.hybrid_orchestrator import HybridOrchestrator
from src.layer2_domain.retrieval.lexical_retriever import LexicalRetriever
from src.layer2_domain.retrieval.service import RetrievalService
from src.layer4_providers.embeddings.mock.adapter import MockEmbedder
from src.layer4_providers.rerankers.mock.adapter import MockReranker
from src.layer4_providers.stores.metadata.sqlite_adapter import SQLiteMetadataStore
from src.layer4_providers.stores.qdrant.adapter import QdrantAdapter
from src.layer4_providers.stores.sqlite_fts.adapter import SQLiteFTSAdapter


@pytest.mark.asyncio
async def test_reranking_service_reorders_candidates_by_relevance() -> None:
    """Reranking should move the most relevant candidate to the front."""
    service = RerankingService(MockReranker())
    candidates = [
        RetrievalCandidate(
            chunk_id="chunk-noisy",
            document_id="doc-1",
            content="Monitoring freshness matters for operations.",
            scores=RetrievalScores(final_score=0.9),
            source=RetrievalSource.HYBRID,
            rank=0,
        ),
        RetrievalCandidate(
            chunk_id="chunk-relevant",
            document_id="doc-2",
            content="Hybrid retrieval diagnostics combine dense and lexical search.",
            scores=RetrievalScores(final_score=0.8),
            source=RetrievalSource.HYBRID,
            rank=1,
        ),
    ]

    reranked, _ = await service.rerank("hybrid retrieval diagnostics", candidates, top_k=2)

    assert reranked[0].chunk_id == "chunk-relevant"
    assert reranked[0].scores.rerank_score is not None


async def build_retrieval_service(tmp_path) -> RetrievalService:
    embedder = MockEmbedder(dimensions=32)
    vector_store = QdrantAdapter(
        url="memory://",
        collection=f"rerank_{uuid.uuid4().hex[:8]}",
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
            id="chunk-relevant",
            document_id="doc-1",
            content="Hybrid retrieval diagnostics combine dense search with lexical BM25.",
            location=ChunkLocation(start_char=0, end_char=68),
            sequence_number=0,
            metadata=ChunkMetadata(document_title="Guide", tags=["rag"], trust_score=0.95, section_title="Guide"),
            created_at=now - timedelta(days=120),
        ),
        Chunk(
            id="chunk-fresh-noisy",
            document_id="doc-2",
            content="Fresh retrieval monitoring notes discuss latency and dashboards.",
            location=ChunkLocation(start_char=0, end_char=62),
            sequence_number=1,
            metadata=ChunkMetadata(document_title="Ops", tags=["ops"], trust_score=0.9, section_title="Ops"),
            created_at=now,
        ),
    ]
    await indexing_service.index_chunks(chunks, document_checksum="rerank-checksum")

    orchestrator = HybridOrchestrator(
        dense_retriever=DenseRetriever(embedder, vector_store, metadata_store),
        lexical_retriever=LexicalRetriever(lexical_store, metadata_store),
        reranking_service=RerankingService(MockReranker()),
        metadata_filter=MetadataFilter(metadata_store),
        freshness_booster=FreshnessBooster(decay_days=15, max_boost=0.5),
        deduplicator=CandidateDeduplicator(),
        diagnostics_store=RetrievalDiagnosticsStore(),
        metadata_store=metadata_store,
        trust_filter=TrustFilter(metadata_store),
    )
    return RetrievalService(orchestrator=orchestrator, default_config=RetrievalConfig(final_top_k=2, rerank_top_k=2))


@pytest.mark.asyncio
async def test_reranking_improves_benchmark_precision(tmp_path) -> None:
    """Benchmark metrics should improve when reranking is enabled."""
    retrieval_service = await build_retrieval_service(tmp_path)
    benchmark = RetrievalBenchmark(
        retrieval_service,
        [{"query": "hybrid retrieval diagnostics", "relevant_chunk_ids": ["chunk-relevant"]}],
    )

    baseline = await benchmark.run(
        RetrievalConfig(final_top_k=1, rerank_enabled=False, apply_freshness_boost=True, rerank_top_k=1)
    )
    reranked = await benchmark.run(
        RetrievalConfig(final_top_k=1, rerank_enabled=True, apply_freshness_boost=True, rerank_top_k=2)
    )

    assert reranked["avg_precision"] > baseline["avg_precision"]
    assert reranked["avg_mrr"] > baseline["avg_mrr"]
