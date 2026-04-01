"""Feature-gated graph retrieval reranking."""

from __future__ import annotations

from typing import Protocol

from src.layer1_contracts.schemas.chunk import Chunk
from src.layer1_contracts.schemas.document import Document
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.retrieval import HybridRetrievalResult
from src.layer1_contracts.schemas.retrieval_config import RetrievalConfig
from src.layer2_domain.graph_retrieval.graph_builder import DocumentGraphBuilder
from src.layer2_domain.graph_retrieval.graph_ranker import GraphAwareRanker
from src.layer2_domain.query_understanding.entity_extractor import EntityExtractor
from src.layer4_providers.stores.graph.networkx_adapter import NetworkXGraphStore


class FeatureFlagReader(Protocol):
    """Minimal protocol for lower-layer feature-flag reads."""

    def is_enabled(self, name: str) -> bool: ...


class RetrievalServiceProtocol(Protocol):
    """Protocol for the standard retrieval path wrapped by graph retrieval."""

    async def retrieve(self, query: Query, config: RetrievalConfig) -> HybridRetrievalResult: ...


class GraphRetrievalService:
    """Apply graph-aware reranking on top of the standard retrieval stack."""

    def __init__(
        self,
        graph_builder: DocumentGraphBuilder,
        feature_flags: FeatureFlagReader,
        standard_retrieval: RetrievalServiceProtocol,
        entity_extractor: EntityExtractor,
        graph_boost: float = 0.15,
        graph_store: NetworkXGraphStore | None = None,
    ) -> None:
        self.graph_builder = graph_builder
        self.feature_flags = feature_flags
        self.standard_retrieval = standard_retrieval
        self.entity_extractor = entity_extractor
        self.graph_boost = graph_boost
        self.graph_store = graph_store or NetworkXGraphStore(path="data/graph.pkl")
        self.diagnostics_store = getattr(standard_retrieval, "diagnostics_store", None)

    def build_graph(self, documents: list[Document], chunks: list[Chunk]) -> None:
        """Build and cache a graph for advanced retrieval."""
        self.graph_store.graph = self.graph_builder.build_graph(documents, chunks)
        self.graph_store.save()

    async def retrieve(self, query: Query, config: RetrievalConfig) -> HybridRetrievalResult:
        """Retrieve normally, then apply graph-aware reranking if enabled."""
        result = await self.standard_retrieval.retrieve(query, config)
        graph = self.graph_store.get_graph()
        if not self.feature_flags.is_enabled("graph_retrieval") or not graph.nodes:
            return result

        entities = [entity.text for entity in self.entity_extractor.extract(query.text)]
        if not entities:
            return result

        reranked = GraphAwareRanker(graph).rerank(result.candidates, entities, boost=self.graph_boost)
        return result.model_copy(update={"candidates": reranked, "total_candidates": len(reranked)})
