"""Hierarchical chunking strategy."""

from __future__ import annotations

from src.layer1_contracts.schemas.chunk import Chunk, ChunkMetadata
from src.layer2_domain.chunking.strategies.base import ChunkingStrategyBase
from src.layer2_domain.chunking.strategies.semantic import SemanticBoundaryStrategy


class HierarchicalStrategy(ChunkingStrategyBase):
    """Create leaf chunks plus parent chunks for grouped sections."""

    def chunk(self, content: str, precursors: list) -> list[Chunk]:
        """Build semantic chunks first, then attach parent chunk relationships."""
        semantic = SemanticBoundaryStrategy(self.config, self.metadata_enricher)
        leaf_chunks = semantic.chunk(content, precursors)
        return self._add_parent_chunks(leaf_chunks)

    def _add_parent_chunks(self, leaf_chunks: list[Chunk]) -> list[Chunk]:
        """Create parent chunks that span sibling chunks within the same section."""
        if len(leaf_chunks) < 3:
            return leaf_chunks

        all_chunks = list(leaf_chunks)
        parent_sequence = len(leaf_chunks)
        section_groups: dict[str, list[Chunk]] = {}

        for chunk in leaf_chunks:
            key = chunk.metadata.section_title or "root"
            section_groups.setdefault(key, []).append(chunk)

        for section, children in section_groups.items():
            if len(children) < 2:
                continue

            parent_content = "\n\n".join(child.content for child in children)
            if len(parent_content) > self.config.max_size * 3:
                continue

            parent_metadata = ChunkMetadata(
                section_title=section,
                section_hierarchy=list(children[0].metadata.section_hierarchy),
                page_numbers=sorted(
                    {
                        page_number
                        for child in children
                        for page_number in child.metadata.page_numbers
                    }
                ),
            )
            parent = self._create_chunk(
                content=parent_content,
                doc_id=children[0].document_id,
                seq=parent_sequence,
                start_char=children[0].location.start_char,
                end_char=children[-1].location.end_char,
                metadata=parent_metadata,
            )
            parent.child_chunk_ids = [child.id for child in children]

            for child in children:
                child.parent_chunk_id = parent.id

            all_chunks.append(parent)
            parent_sequence += 1

        return all_chunks
