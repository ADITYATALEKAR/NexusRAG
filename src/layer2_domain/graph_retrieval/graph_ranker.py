"""Graph-aware reranking."""

from __future__ import annotations

import networkx as nx

from src.layer1_contracts.schemas.retrieval import RetrievalCandidate


class GraphAwareRanker:
    """Boost retrieval candidates connected to query entities in the graph."""

    def __init__(self, graph: nx.DiGraph) -> None:
        self.graph = graph

    def rerank(
        self,
        candidates: list[RetrievalCandidate],
        query_entities: list[str],
        boost: float = 0.15,
    ) -> list[RetrievalCandidate]:
        """Return candidates reranked using graph connectivity signals."""
        entity_nodes = [f"entity:{entity.lower()}" for entity in query_entities]
        reranked = [candidate.model_copy(deep=True) for candidate in candidates]
        for candidate in reranked:
            for entity_node in entity_nodes:
                if self.graph.has_edge(candidate.chunk_id, entity_node):
                    weight = float(self.graph[candidate.chunk_id][entity_node].get("weight", 1.0))
                    candidate.scores.final_score += boost * weight
            candidate.rank = 0
        reranked.sort(key=lambda candidate: candidate.scores.final_score, reverse=True)
        for index, candidate in enumerate(reranked):
            candidate.rank = index
        return reranked
