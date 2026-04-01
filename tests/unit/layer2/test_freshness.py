"""Tests for Phase 2 freshness tracking."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.layer1_contracts.schemas.indexing import IndexState
from src.layer2_domain.indexing.freshness import FreshnessTracker
from src.layer4_providers.stores.metadata.sqlite_adapter import SQLiteMetadataStore


@pytest.mark.asyncio
async def test_freshness_tracker_detects_checksum_changes_and_stale_flags(tmp_path) -> None:
    """Freshness checks should require reindexing for changed or stale documents."""
    metadata_store = SQLiteMetadataStore(db_path=str(tmp_path / "metadata.db"))
    tracker = FreshnessTracker(metadata_store)

    await metadata_store.save_index_state(
        IndexState(
            document_id="doc-1",
            document_checksum="checksum-1",
            indexed_at=datetime.now(timezone.utc),
            chunk_count=2,
            embedding_model="mock-embed",
        )
    )

    assert not await tracker.needs_reindex("doc-1", "checksum-1")
    assert await tracker.needs_reindex("doc-1", "checksum-2")

    await tracker.mark_stale("doc-1")
    assert await tracker.needs_reindex("doc-1", "checksum-1")
    assert "doc-1" in await tracker.get_stale_documents()
