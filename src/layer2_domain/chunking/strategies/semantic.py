"""Semantic boundary chunking strategy."""

from __future__ import annotations

import re

from src.layer1_contracts.schemas.chunk import Chunk
from src.layer2_domain.chunking.strategies.base import ChunkingStrategyBase


class SemanticBoundaryStrategy(ChunkingStrategyBase):
    """Chunk content at semantic boundaries such as sections and paragraphs."""

    PARAGRAPH_PATTERN = re.compile(r"\n\n+")

    def chunk(self, content: str, precursors: list) -> list[Chunk]:
        """Chunk content using precursor boundaries when available."""
        chunks: list[Chunk] = []
        sequence = 0

        if precursors:
            for precursor in precursors:
                precursor_chunks = self._chunk_precursor(precursor, sequence)
                chunks.extend(precursor_chunks)
                sequence += len(precursor_chunks)
            return chunks

        return self._chunk_by_paragraphs(content, "", 0, sequence)

    def _chunk_precursor(self, precursor, start_seq: int) -> list[Chunk]:
        """Chunk one precursor while preserving its metadata."""
        content = precursor.content
        metadata = self.metadata_enricher.from_precursor(precursor)

        if len(content) <= self.config.max_size:
            return [
                self._create_chunk(
                    content=content,
                    doc_id=precursor.document_id,
                    seq=start_seq,
                    start_char=precursor.start_char,
                    end_char=precursor.end_char,
                    metadata=metadata,
                )
            ]

        if precursor.suggested_split_points:
            return self._split_at_points(precursor, start_seq, metadata)

        return self._split_by_paragraphs(precursor, start_seq, metadata)

    def _split_at_points(self, precursor, start_seq: int, metadata) -> list[Chunk]:
        """Split a precursor using suggested split points from Phase 1."""
        chunks: list[Chunk] = []
        content = precursor.content
        points = [0] + list(precursor.suggested_split_points) + [len(content)]
        sequence = start_seq

        for index in range(len(points) - 1):
            start, end = points[index], points[index + 1]
            chunk_content = content[start:end].strip()

            if len(chunk_content) < self.config.min_size and chunks:
                previous = chunks[-1]
                merged_content = previous.content + "\n" + chunk_content
                chunks[-1] = self._create_chunk(
                    content=merged_content,
                    doc_id=precursor.document_id,
                    seq=previous.sequence_number,
                    start_char=previous.location.start_char,
                    end_char=precursor.start_char + end,
                    metadata=previous.metadata,
                )
            elif len(chunk_content) >= self.config.min_size:
                chunks.append(
                    self._create_chunk(
                        content=chunk_content,
                        doc_id=precursor.document_id,
                        seq=sequence,
                        start_char=precursor.start_char + start,
                        end_char=precursor.start_char + end,
                        metadata=metadata.model_copy(deep=True),
                    )
                )
                sequence += 1

        return chunks

    def _split_by_paragraphs(self, precursor, start_seq: int, metadata) -> list[Chunk]:
        """Split a precursor by paragraph boundaries when explicit split points are absent."""
        paragraphs = [paragraph.strip() for paragraph in self.PARAGRAPH_PATTERN.split(precursor.content)]
        chunks: list[Chunk] = []
        current_content = ""
        current_start = precursor.start_char
        search_from = 0
        sequence = start_seq

        for paragraph in paragraphs:
            if not paragraph:
                continue

            paragraph_index = precursor.content.find(paragraph, search_from)
            if paragraph_index < 0:
                paragraph_index = search_from
            search_from = paragraph_index + len(paragraph)

            separator = "\n\n" if current_content else ""
            candidate = f"{current_content}{separator}{paragraph}"
            if len(candidate) <= self.config.target_size or not current_content:
                current_content = candidate
                if not chunks and not current_content.strip():
                    current_start = precursor.start_char + paragraph_index
            else:
                chunks.append(
                    self._create_chunk(
                        content=current_content,
                        doc_id=precursor.document_id,
                        seq=sequence,
                        start_char=current_start,
                        end_char=current_start + len(current_content),
                        metadata=metadata.model_copy(deep=True),
                    )
                )
                sequence += 1
                current_content = paragraph
                current_start = precursor.start_char + paragraph_index

        if current_content:
            chunks.append(
                self._create_chunk(
                    content=current_content,
                    doc_id=precursor.document_id,
                    seq=sequence,
                    start_char=current_start,
                    end_char=current_start + len(current_content),
                    metadata=metadata.model_copy(deep=True),
                )
            )

        return chunks

    def _chunk_by_paragraphs(self, content: str, doc_id: str, base_start: int, start_seq: int) -> list[Chunk]:
        """Fallback paragraph chunking for content without precursors."""
        precursor = type(
            "PrecursorProxy",
            (),
            {
                "content": content,
                "document_id": doc_id,
                "start_char": base_start,
                "end_char": base_start + len(content),
                "section_title": None,
                "section_hierarchy": [],
                "page_numbers": [],
                "content_type": "text",
                "suggested_split_points": [],
            },
        )()
        metadata = self.metadata_enricher.from_precursor(None)
        return self._split_by_paragraphs(precursor, start_seq, metadata)
