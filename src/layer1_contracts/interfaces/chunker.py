"""Chunker interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.layer1_contracts.schemas.chunk import Chunk
from src.layer1_contracts.schemas.document import Document


class ChunkerInterface(ABC):
    """Abstract interface for document chunking."""

    @abstractmethod
    async def chunk(self, document: Document) -> list[Chunk]:
        """Chunk a document into retrievable units."""
