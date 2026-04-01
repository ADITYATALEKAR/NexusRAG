"""Abstract interface for chunk/document metadata stores."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.layer1_contracts.schemas.chunk import Chunk
from src.layer1_contracts.schemas.document import Document
from src.layer1_contracts.schemas.indexing import IndexState


class MetadataStoreInterface(ABC):
    """Abstract metadata storage contract for chunk and document state."""

    @abstractmethod
    async def save_chunk(self, chunk: Chunk) -> None:
        """Persist metadata for one chunk."""

    @abstractmethod
    async def get_chunk(self, chunk_id: str) -> dict | None:
        """Return stored metadata for one chunk."""

    @abstractmethod
    async def list_chunks(self) -> list[Chunk]:
        """Return every stored chunk."""

    @abstractmethod
    async def list_documents(self) -> list[Document]:
        """Return every stored document."""

    @abstractmethod
    async def save_index_state(self, state: IndexState) -> None:
        """Persist index state for one document."""

    @abstractmethod
    async def get_index_state(self, document_id: str) -> IndexState | None:
        """Return the current index state for one document."""

    @abstractmethod
    async def mark_stale(self, document_id: str) -> None:
        """Mark an indexed document as stale."""

    @abstractmethod
    async def get_stale_documents(self) -> list[str]:
        """Return the identifiers of stale indexed documents."""

    @abstractmethod
    async def delete_document(self, document_id: str) -> int:
        """Delete stored metadata for one document and return removed chunk count."""
