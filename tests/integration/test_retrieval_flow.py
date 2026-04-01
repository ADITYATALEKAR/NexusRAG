"""Integration tests for the retrieval flow and API routes."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.routes.retrieval import _build_retrieval_stack, router as retrieval_router
from src.layer1_contracts.schemas.chunk import Chunk, ChunkLocation, ChunkMetadata
from src.layer1_contracts.schemas.query import Query, QueryFilters
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
from src.layer3_flows.retrieval_flow.flow import RetrievalFlow
from src.layer4_providers.embeddings.mock.adapter import MockEmbedder
from src.layer4_providers.rerankers.mock.adapter import MockReranker
from src.layer4_providers.stores.metadata.sqlite_adapter import SQLiteMetadataStore
from src.layer4_providers.stores.qdrant.adapter import QdrantAdapter
from src.layer4_providers.stores.sqlite_fts.adapter import SQLiteFTSAdapter


def write_config(path: Path, content: str) -> None:
    """Write a YAML fixture to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


async def build_retrieval_stack(tmp_path) -> tuple[RetrievalService, RetrievalFlow]:
    embedder = MockEmbedder(dimensions=32)
    vector_store = QdrantAdapter(
        url="memory://",
        collection=f"retrieval_{uuid.uuid4().hex[:8]}",
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
            id="chunk-hybrid-core",
            document_id="doc-1",
            content="Hybrid retrieval uses dense vectors, BM25, fusion, and reranking.",
            location=ChunkLocation(start_char=0, end_char=67),
            sequence_number=0,
            metadata=ChunkMetadata(
                document_title="Hybrid Core",
                document_type="md",
                tags=["rag", "hybrid"],
                trust_score=0.95,
                section_title="Core",
                page_numbers=[1],
            ),
            created_at=now - timedelta(days=60),
        ),
        Chunk(
            id="chunk-security",
            document_id="doc-2",
            content="Security policies cover request signing, masking, and audit events.",
            location=ChunkLocation(start_char=0, end_char=68),
            sequence_number=1,
            metadata=ChunkMetadata(
                document_title="Security",
                document_type="md",
                tags=["security"],
                trust_score=0.92,
                section_title="Security",
                page_numbers=[2],
            ),
            created_at=now,
        ),
    ]
    await indexing_service.index_chunks(chunks, document_checksum="retrieval-flow")

    retrieval_service = RetrievalService(
        orchestrator=HybridOrchestrator(
            dense_retriever=DenseRetriever(embedder, vector_store, metadata_store),
            lexical_retriever=LexicalRetriever(lexical_store, metadata_store),
            reranking_service=RerankingService(MockReranker()),
            metadata_filter=MetadataFilter(metadata_store),
            freshness_booster=FreshnessBooster(),
            deduplicator=CandidateDeduplicator(),
            diagnostics_store=RetrievalDiagnosticsStore(),
            metadata_store=metadata_store,
            trust_filter=TrustFilter(metadata_store),
        ),
        default_config=RetrievalConfig(final_top_k=2, rerank_top_k=2),
    )
    return retrieval_service, RetrievalFlow(retrieval_service)


@pytest.mark.asyncio
async def test_retrieval_flow_returns_diagnostics_for_each_stage(tmp_path) -> None:
    """End-to-end retrieval should produce stage diagnostics and final candidates."""
    retrieval_service, flow = await build_retrieval_stack(tmp_path)

    result = await flow.execute(
        Query(
            id="query-1",
            text="hybrid retrieval reranking",
            filters=QueryFilters(tags=["rag"]),
        )
    )

    assert result.candidates
    assert result.candidates[0].chunk_id == "chunk-hybrid-core"
    assert result.diagnostics is not None
    assert result.diagnostics.dense_result is not None
    assert result.diagnostics.lexical_result is not None
    assert result.diagnostics.fusion_result is not None
    assert result.diagnostics.filter_result is not None


@pytest.mark.asyncio
async def test_retrieval_api_endpoints_are_functional(tmp_path) -> None:
    """The retrieval API should execute queries and expose cached diagnostics."""
    retrieval_service, flow = await build_retrieval_stack(tmp_path)
    app = FastAPI()
    app.include_router(retrieval_router, prefix="/retrieval")
    app.state.retrieval_service = retrieval_service
    app.state.retrieval_flow = flow

    with TestClient(app) as client:
        response = client.post(
            "/retrieval/retrieve",
            json={
                "query": "hybrid retrieval reranking",
                "top_k": 2,
                "rerank": True,
                "filters": {"tags": ["rag"]},
                "include_diagnostics": True,
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] >= 1
        assert payload["candidates"][0]["chunk_id"] == "chunk-hybrid-core"
        assert payload["diagnostics"]["fusion_result"]["count"] >= 1

        diagnostics = client.get(f"/retrieval/diagnostics/{payload['query_id']}")
        assert diagnostics.status_code == 200
        assert diagnostics.json()["query_id"] == payload["query_id"]


@pytest.mark.asyncio
async def test_app_retrieval_builder_loads_phase6_flags_and_graph_store(tmp_path) -> None:
    """The app retrieval builder should honor Phase 6 config and persist the graph store."""
    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    write_config(
        config_dir / "retrieval" / "retrieval.yaml",
        "\n".join(
            [
                "retrieval:",
                '  default_mode: "hybrid"',
                "  dense_top_k: 10",
                "  lexical_top_k: 10",
                "  fusion_top_k: 5",
                "  final_top_k: 2",
                "  freshness_decay_days: 30",
            ]
        ),
    )
    write_config(
        config_dir / "retrieval" / "fusion.yaml",
        "\n".join(
            [
                "fusion:",
                '  method: "rrf"',
                "  rrf_k: 60",
                "  dense_weight: 0.5",
                "  lexical_weight: 0.5",
            ]
        ),
    )
    write_config(
        config_dir / "retrieval" / "reranking.yaml",
        "\n".join(
            [
                "reranking:",
                "  enabled: false",
                '  provider: "mock"',
                "  top_k: 5",
            ]
        ),
    )
    write_config(
        config_dir / "feature_flags.yaml",
        "\n".join(
            [
                "contextual_indexing:",
                '  status: "disabled"',
                "graph_retrieval:",
                '  status: "enabled"',
                "vector_compression:",
                '  status: "disabled"',
            ]
        ),
    )
    write_config(
        config_dir / "advanced" / "graph.yaml",
        "\n".join(
            [
                "max_hops: 2",
                "max_nodes: 50",
                "boost_factor: 0.20",
            ]
        ),
    )
    write_config(
        config_dir / "advanced" / "compression.yaml",
        "\n".join(
            [
                "default_method: scalar",
                "scalar:",
                "  enabled: true",
                "product_quantization:",
                "  num_subvectors: 8",
                "  num_centroids: 16",
            ]
        ),
    )

    embedder = MockEmbedder(dimensions=32)
    vector_store = QdrantAdapter(
        url=str(data_dir / "qdrant"),
        collection="retrieval_chunks",
        dimensions=embedder.dimensions,
    )
    lexical_store = SQLiteFTSAdapter(db_path=str(data_dir / "lexical.db"))
    metadata_store = SQLiteMetadataStore(db_path=str(data_dir / "metadata.db"))
    indexing_service = IndexingService(
        embedder=embedder,
        vector_store=vector_store,
        lexical_store=lexical_store,
        metadata_store=metadata_store,
    )
    chunks = [
        Chunk(
            id="chunk-google-001",
            document_id="document-01",
            content="Google released the first Pixel phone.",
            location=ChunkLocation(start_char=0, end_char=38),
            sequence_number=0,
            metadata=ChunkMetadata(document_title="Pixel History"),
        ),
        Chunk(
            id="chunk-google-002",
            document_id="document-01",
            content="Pixel devices expanded hardware efforts across the company.",
            location=ChunkLocation(start_char=39, end_char=96),
            sequence_number=1,
            metadata=ChunkMetadata(document_title="Pixel History"),
        ),
    ]
    await indexing_service.index_chunks(chunks, document_checksum="phase6-runtime")
    vector_store.client.close()

    retrieval_service, _flow = _build_retrieval_stack(config_dir)
    candidates = await retrieval_service.retrieve_simple("Google release", top_k=2)

    assert candidates[0].chunk_id == "chunk-google-001"
    assert (data_dir / "graph.pkl").exists()
