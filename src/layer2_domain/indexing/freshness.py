"""Freshness tracking for index state."""

from __future__ import annotations

from typing import Protocol


class IndexStateStoreProtocol(Protocol):
    """Protocol for metadata stores that persist index state."""

    async def get_index_state(self, document_id: str): ...
    async def mark_stale(self, document_id: str) -> None: ...
    async def get_stale_documents(self) -> list[str]: ...


class FreshnessTracker:
    """Determine whether a document requires reindexing."""

    def __init__(self, metadata_store: IndexStateStoreProtocol):
        self.metadata_store = metadata_store

    async def needs_reindex(self, document_id: str, current_checksum: str) -> bool:
        """Return whether the document should be reindexed."""
        state = await self.metadata_store.get_index_state(document_id)
        if state is None:
            return True
        if state.is_stale:
            return True
        if state.document_checksum != current_checksum:
            return True
        return False

    async def mark_stale(self, document_id: str) -> None:
        """Mark a document as stale."""
        await self.metadata_store.mark_stale(document_id)

    async def get_stale_documents(self) -> list[str]:
        """Return all currently stale document ids."""
        return await self.metadata_store.get_stale_documents()
