"""Graph construction for document, chunk, and entity relationships."""

from __future__ import annotations

from collections import defaultdict

import networkx as nx

from src.layer1_contracts.schemas.chunk import Chunk
from src.layer1_contracts.schemas.document import Document
from src.layer1_contracts.schemas.graph import EdgeType, NodeType
from src.layer2_domain.query_understanding.entity_extractor import EntityExtractor


class DocumentGraphBuilder:
    """Build a directed graph over documents, chunks, and extracted entities."""

    def __init__(self, entity_extractor: EntityExtractor) -> None:
        self.entity_extractor = entity_extractor

    def build_graph(self, documents: list[Document], chunks: list[Chunk]) -> nx.DiGraph:
        """Return a directed graph linking documents, chunks, and entities."""
        graph = nx.DiGraph()
        chunks_by_document: dict[str, list[Chunk]] = defaultdict(list)

        for document in documents:
            graph.add_node(
                document.id,
                node_type=NodeType.DOCUMENT.value,
                content=document.content[:500],
            )

        for chunk in chunks:
            chunks_by_document[chunk.document_id].append(chunk)
            graph.add_node(
                chunk.id,
                node_type=NodeType.CHUNK.value,
                content=chunk.content,
                document_id=chunk.document_id,
            )
            graph.add_edge(chunk.document_id, chunk.id, edge_type=EdgeType.CONTAINS.value, weight=1.0)

        for document_id, ordered_chunks in chunks_by_document.items():
            del document_id
            ordered_chunks.sort(key=lambda chunk: chunk.sequence_number)
            for previous, current in zip(ordered_chunks, ordered_chunks[1:]):
                graph.add_edge(previous.id, current.id, edge_type=EdgeType.FOLLOWS.value, weight=1.0)

        entity_to_chunks: dict[str, list[str]] = defaultdict(list)
        for chunk in chunks:
            for entity in self.entity_extractor.extract(chunk.content):
                entity_id = f"entity:{entity.text.lower()}"
                graph.add_node(
                    entity_id,
                    node_type=NodeType.ENTITY.value,
                    content=entity.text,
                    entity_type=entity.entity_type,
                )
                graph.add_edge(chunk.id, entity_id, edge_type=EdgeType.REFERENCES.value, weight=entity.confidence)
                graph.add_edge(entity_id, chunk.id, edge_type=EdgeType.REFERENCES.value, weight=entity.confidence)
                entity_to_chunks[entity_id].append(chunk.id)

        entity_ids = sorted(entity_to_chunks)
        for index, left_id in enumerate(entity_ids):
            left_chunks = set(entity_to_chunks[left_id])
            for right_id in entity_ids[index + 1 :]:
                shared = left_chunks & set(entity_to_chunks[right_id])
                if not shared:
                    continue
                weight = len(shared) / max(len(left_chunks), len(entity_to_chunks[right_id]))
                graph.add_edge(left_id, right_id, edge_type=EdgeType.RELATED_TO.value, weight=weight)
                graph.add_edge(right_id, left_id, edge_type=EdgeType.RELATED_TO.value, weight=weight)

        return graph
