"""Fixed-size chunking strategy."""

from __future__ import annotations

from src.layer1_contracts.schemas.chunk import Chunk
from src.layer2_domain.chunking.strategies.base import ChunkingStrategyBase


class FixedSizeStrategy(ChunkingStrategyBase):
    """Simple fixed-size chunking with overlap-aware windowing."""

    def chunk(self, content: str, precursors: list) -> list[Chunk]:
        """Create fixed-size chunks across precursors or raw content."""
        if precursors:
            chunks: list[Chunk] = []
            sequence = 0
            for precursor in precursors:
                metadata = self.metadata_enricher.from_precursor(precursor)
                precursor_chunks = self._chunk_span(
                    precursor.content,
                    precursor.document_id,
                    precursor.start_char,
                    sequence,
                    metadata,
                )
                chunks.extend(precursor_chunks)
                sequence += len(precursor_chunks)
            return chunks

        return self._chunk_span(content, "", 0, 0, self.metadata_enricher.from_precursor(None))

    def _chunk_span(
        self,
        content: str,
        doc_id: str,
        base_start: int,
        start_seq: int,
        metadata,
    ) -> list[Chunk]:
        """Chunk a single content span using fixed windows."""
        chunks: list[Chunk] = []
        position = 0
        sequence = start_seq

        while position < len(content):
            end = min(position + self.config.target_size, len(content))
            if self.config.preserve_sentences and end < len(content):
                end = self._find_sentence_boundary(content, position, end)

            chunk_content = content[position:end].strip()
            if len(chunk_content) >= self.config.min_size:
                chunks.append(
                    self._create_chunk(
                        content=chunk_content,
                        doc_id=doc_id,
                        seq=sequence,
                        start_char=base_start + position,
                        end_char=base_start + end,
                        metadata=metadata.model_copy(deep=True),
                    )
                )
                sequence += 1

            next_position = end - self.config.overlap
            if next_position <= position:
                next_position = end
            position = next_position

        return chunks

    def _find_sentence_boundary(self, text: str, start: int, target: int) -> int:
        """Find the nearest sentence boundary before the target window end."""
        search_region = text[start : target + 100]
        for pattern in [". ", ".\n", "! ", "? "]:
            last_index = search_region.rfind(pattern, 0, target - start + 50)
            if last_index > 0:
                return start + last_index + len(pattern)
        return target
