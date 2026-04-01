"""Base chunking strategy."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.layer0_core.ids.base import ChunkId
from src.layer1_contracts.schemas.chunk import Chunk, ChunkLocation, ChunkMetadata
from src.layer1_contracts.schemas.chunking import ChunkingConfig
from src.layer2_domain.chunking.metadata_enricher import ChunkMetadataEnricher


class ChunkingStrategyBase(ABC):
    """Abstract base class for chunking strategies."""

    def __init__(
        self,
        config: ChunkingConfig,
        metadata_enricher: ChunkMetadataEnricher | None = None,
    ) -> None:
        self.config = config
        self.metadata_enricher = metadata_enricher or ChunkMetadataEnricher()

    @abstractmethod
    def chunk(self, content: str, precursors: list) -> list[Chunk]:
        """Split content into retrieval-ready chunks."""

    def _create_chunk(
        self,
        content: str,
        doc_id: str,
        seq: int,
        start_char: int,
        end_char: int,
        metadata: ChunkMetadata,
    ) -> Chunk:
        """Create a typed chunk object with traceable offsets."""
        page_numbers = metadata.page_numbers
        start_page = min(page_numbers) if page_numbers else None
        end_page = max(page_numbers) if page_numbers else None
        return Chunk(
            id=ChunkId.generate().value,
            document_id=doc_id,
            content=content,
            location=ChunkLocation(
                start_char=start_char,
                end_char=end_char,
                start_page=start_page,
                end_page=end_page,
            ),
            sequence_number=seq,
            metadata=metadata,
            token_count=len(content.split()),
        )
