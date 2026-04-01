"""Unit tests for Phase 6 graph retrieval."""

from __future__ import annotations

import pytest

from src.layer1_contracts.schemas.chunk import Chunk, ChunkLocation, ChunkMetadata
from src.layer1_contracts.schemas.document import Document, DocumentType
from src.layer1_contracts.schemas.feature_flags import FeatureFlag, FeatureStatus
from src.layer1_contracts.schemas.graph import GraphQuery
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.retrieval import (
    HybridRetrievalResult,
    RetrievalCandidate,
    RetrievalDiagnostics,
    RetrievalScores,
    RetrievalSource,
)
from src.layer1_contracts.schemas.retrieval_config import RetrievalConfig
from src.layer2_domain.graph_retrieval.graph_builder import DocumentGraphBuilder
from src.layer2_domain.graph_retrieval.graph_ranker import GraphAwareRanker
from src.layer2_domain.graph_retrieval.service import GraphRetrievalService
from src.layer2_domain.graph_retrieval.traversal import GraphTraversal
from src.layer2_domain.query_understanding.entity_extractor import EntityExtractor
from src.layer8_runtime.feature_flags.manager import FeatureFlagManager


class StubRetrievalService:
    """Baseline retrieval stub for graph retrieval tests."""

    def __init__(self, candidates: list[RetrievalCandidate]) -> None:
        self._candidates = candidates

    async def retrieve(self, query: Query, config: RetrievalConfig) -> HybridRetrievalResult:
        del config
        return HybridRetrievalResult(
            query_id=query.id,
            candidates=[candidate.model_copy(deep=True) for candidate in self._candidates],
            total_candidates=len(self._candidates),
            diagnostics=RetrievalDiagnostics(
                query_id=query.id,
                query_text=query.text,
                query_embedding_time_ms=1,
                final_candidates=[candidate.model_copy(deep=True) for candidate in self._candidates],
                total_latency_ms=1,
                config=RetrievalConfig(),
            ),
            dense_latency_ms=1,
            lexical_latency_ms=1,
            fusion_latency_ms=1,
            filter_latency_ms=1,
            rerank_latency_ms=1,
            total_latency_ms=1,
        )


def _documents() -> list[Document]:
    return [
        Document(
            id="document-01",
            content="Google introduced Pixel devices and vector search guidance.",
            document_type=DocumentType.MD,
        )
    ]


def _chunks() -> list[Chunk]:
    return [
        Chunk(
            id="chunk-0001",
            document_id="document-01",
            content="Google released the first Pixel phone.",
            location=ChunkLocation(start_char=0, end_char=38),
            sequence_number=0,
            metadata=ChunkMetadata(document_title="Pixel History"),
        ),
        Chunk(
            id="chunk-0002",
            document_id="document-01",
            content="Pixel devices helped expand hardware efforts.",
            location=ChunkLocation(start_char=39, end_char=93),
            sequence_number=1,
            metadata=ChunkMetadata(document_title="Pixel History"),
        ),
    ]


def _candidates() -> list[RetrievalCandidate]:
    return [
        RetrievalCandidate(
            chunk_id="chunk-0002",
            document_id="document-01",
            content="Pixel devices helped expand hardware efforts.",
            scores=RetrievalScores(final_score=0.70),
            source=RetrievalSource.HYBRID,
            rank=1,
        ),
        RetrievalCandidate(
            chunk_id="chunk-0001",
            document_id="document-01",
            content="Google released the first Pixel phone.",
            scores=RetrievalScores(final_score=0.70),
            source=RetrievalSource.HYBRID,
            rank=0,
        ),
    ]


def test_document_graph_builder_creates_document_chunk_entity_edges() -> None:
    """Graph builder should connect documents, chunks, and extracted entities."""
    builder = DocumentGraphBuilder(EntityExtractor())

    graph = builder.build_graph(_documents(), _chunks())

    assert graph.has_edge("document-01", "chunk-0001")
    assert graph.has_edge("chunk-0001", "entity:google")
    assert graph.has_edge("entity:pixel", "chunk-0002")


def test_graph_traversal_finds_related_chunk_via_entity() -> None:
    """Traversal should discover related chunks through entity links."""
    graph = DocumentGraphBuilder(EntityExtractor()).build_graph(_documents(), _chunks())
    traversal = GraphTraversal(graph)

    nodes = traversal.traverse(GraphQuery(seed_nodes=["chunk-0001"], max_hops=2, max_nodes=10))

    node_ids = [node.id for node in nodes]
    assert "chunk-0002" in node_ids


def test_graph_aware_ranker_boosts_connected_candidate() -> None:
    """Candidates linked to query entities should receive a score boost."""
    graph = DocumentGraphBuilder(EntityExtractor()).build_graph(_documents(), _chunks())
    ranker = GraphAwareRanker(graph)

    reranked = ranker.rerank(_candidates(), ["Google"], boost=0.20)

    assert reranked[0].chunk_id == "chunk-0001"
    assert reranked[0].scores.final_score > 0.70


@pytest.mark.asyncio
async def test_graph_retrieval_service_respects_feature_flag() -> None:
    """Graph retrieval should be a no-op when disabled and rerank when enabled."""
    builder = DocumentGraphBuilder(EntityExtractor())
    baseline = StubRetrievalService(_candidates())
    query = Query(id="query-graph-1", text="What did Google release?")
    config = RetrievalConfig()

    disabled_service = GraphRetrievalService(
        graph_builder=builder,
        feature_flags=FeatureFlagManager(
            flags=[FeatureFlag(name="graph_retrieval", status=FeatureStatus.DISABLED)]
        ),
        standard_retrieval=baseline,
        entity_extractor=EntityExtractor(),
    )
    disabled_service.build_graph(_documents(), _chunks())
    disabled_result = await disabled_service.retrieve(query, config)

    enabled_service = GraphRetrievalService(
        graph_builder=builder,
        feature_flags=FeatureFlagManager(
            flags=[FeatureFlag(name="graph_retrieval", status=FeatureStatus.ENABLED)]
        ),
        standard_retrieval=baseline,
        entity_extractor=EntityExtractor(),
    )
    enabled_service.build_graph(_documents(), _chunks())
    enabled_result = await enabled_service.retrieve(query, config)

    assert disabled_result.candidates[0].chunk_id == "chunk-0002"
    assert enabled_result.candidates[0].chunk_id == "chunk-0001"
