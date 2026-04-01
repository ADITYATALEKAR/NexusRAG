"""Persistent NetworkX graph storage adapter."""

from __future__ import annotations

import pickle
from pathlib import Path

import networkx as nx


class NetworkXGraphStore:
    """Persist a directed graph to disk using pickle for local experimentation."""

    def __init__(self, path: str = "data/graph.pkl") -> None:
        self.path = Path(path)
        self.graph = nx.DiGraph()
        if self.path.exists():
            with self.path.open("rb") as handle:
                self.graph = pickle.load(handle)

    def save(self) -> None:
        """Persist the current graph state to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("wb") as handle:
            pickle.dump(self.graph, handle)

    def add_node(self, node_id: str, **attrs) -> None:
        """Add or update a node."""
        self.graph.add_node(node_id, **attrs)

    def add_edge(self, source_id: str, target_id: str, **attrs) -> None:
        """Add or update a directed edge."""
        self.graph.add_edge(source_id, target_id, **attrs)

    def get_neighbors(self, node_id: str) -> list[str]:
        """Return all outgoing neighbors for a node."""
        if not self.graph.has_node(node_id):
            return []
        return list(self.graph.successors(node_id))

    def get_graph(self) -> nx.DiGraph:
        """Return the underlying graph object."""
        return self.graph
