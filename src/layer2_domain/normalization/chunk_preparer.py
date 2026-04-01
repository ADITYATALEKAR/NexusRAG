"""Chunk precursor preparation."""

from __future__ import annotations

import re

from src.layer1_contracts.schemas.normalization import ChunkPrecursor, NormalizedDocument, NormalizedSection


class ChunkPreparer:
    """Prepare normalized sections for the chunking phase."""

    def __init__(self, target_size: int = 512, min_size: int = 64) -> None:
        self.target_size = target_size
        self.min_size = min_size

    def prepare(self, normalized_doc: NormalizedDocument) -> list[ChunkPrecursor]:
        """Convert normalized sections into chunk precursors."""
        precursors: list[ChunkPrecursor] = []
        section_map = {section.id: section for section in normalized_doc.sections}
        for section in normalized_doc.sections:
            precursor = self._section_to_precursor(section, normalized_doc.id, section_map)
            if len(section.content) > self.target_size:
                precursor.suggested_split_points = self._find_split_points(section.content)
            precursor.is_complete_section = len(section.content) <= self.target_size
            precursors.append(precursor)
        return precursors

    def _section_to_precursor(
        self,
        section: NormalizedSection,
        doc_id: str,
        section_map: dict[str, NormalizedSection],
    ) -> ChunkPrecursor:
        """Convert one section into a precursor object."""
        return ChunkPrecursor(
            id=f"pre-{section.id}",
            document_id=doc_id,
            content=section.content,
            section_id=section.id,
            section_title=section.title,
            section_hierarchy=self._get_hierarchy(section, section_map),
            content_type=section.content_type,
            start_char=section.start_char,
            end_char=section.end_char,
            page_numbers=section.page_numbers,
        )

    def _find_split_points(self, text: str) -> list[int]:
        """Find natural split points using paragraph and sentence boundaries."""
        points: list[int] = []
        for match in re.finditer(r"\n\n+", text):
            points.append(match.start())
        for match in re.finditer(r"[.!?]\s+", text):
            position = match.end()
            if not any(abs(position - point) < 100 for point in points):
                points.append(position)
        points.sort()
        return points

    def _get_hierarchy(
        self,
        section: NormalizedSection,
        section_map: dict[str, NormalizedSection],
    ) -> list[str]:
        """Build section hierarchy titles from the parent chain."""
        hierarchy: list[str] = []
        current: NormalizedSection | None = section
        while current is not None:
            if current.title:
                hierarchy.append(current.title)
            current = section_map.get(current.parent_id) if current.parent_id else None
        hierarchy.reverse()
        return hierarchy
