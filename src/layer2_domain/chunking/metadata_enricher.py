"""Chunk metadata enrichment helpers."""

from __future__ import annotations

from src.layer1_contracts.schemas.chunk import ChunkMetadata
from src.layer1_contracts.schemas.normalization import ChunkPrecursor


class ChunkMetadataEnricher:
    """Build chunk metadata from chunk precursors."""

    def from_precursor(self, precursor: ChunkPrecursor | None) -> ChunkMetadata:
        """Create metadata for a chunk based on its precursor context."""
        if precursor is None:
            return ChunkMetadata()

        return ChunkMetadata(
            section_title=precursor.section_title,
            section_hierarchy=list(precursor.section_hierarchy),
            page_numbers=list(precursor.page_numbers),
            is_table=precursor.content_type == "table",
            is_code=precursor.content_type == "code",
        )
