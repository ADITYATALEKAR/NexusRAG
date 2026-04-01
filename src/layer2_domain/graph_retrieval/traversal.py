"""Graph traversal helpers."""

from __future__ import annotations

from collections import deque

import networkx as nx

from src.layer1_contracts.schemas.graph import GraphNode, GraphQuery, NodeType


class GraphTraversal:
    """Breadth-first traversal over a graph retrieval index."""

    def __init__(self, graph: nx.DiGraph) -> None:
        self.graph = graph

    def traverse(self, query: GraphQuery) -> list[GraphNode]:
        """Traverse outward from seed nodes within the configured bounds."""
        visited: set[str] = set()
        results: list[GraphNode] = []
        queue: deque[tuple[str, int]] = deque((seed, 0) for seed in query.seed_nodes)

        while queue and len(results) < query.max_nodes:
            node_id, depth = queue.popleft()
            if node_id in visited or depth > query.max_hops or not self.graph.has_node(node_id):
                continue
            visited.add(node_id)
            data = self.graph.nodes[node_id]
            node_type = NodeType(data.get("node_type", NodeType.CHUNK.value))
            results.append(GraphNode(id=node_id, node_type=node_type, content=data.get("content")))
            for _, target, _ in self.graph.out_edges(node_id, data=True):
                queue.append((target, depth + 1))

        return results
