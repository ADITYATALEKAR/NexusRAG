"""Tests for retrieval filters."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from src.layer1_contracts.schemas.chunk import Chunk, ChunkLocation, ChunkMetadata
from src.layer1_contracts.schemas.retrieval import RetrievalCandidate, RetrievalScores, RetrievalSource
from src.layer1_contracts.schemas.retrieval_config import FilterConfig
from src.layer2_domain.retrieval.filters.freshness_filter import FreshnessBooster
from src.layer2_domain.retrieval.filters.metadata_filter import MetadataFilter
from src.layer2_domain.retrieval.filters.trust_filter import TrustFilter
from src.layer4_providers.stores.metadata.sqlite_adapter import SQLiteMetadataStore


def make_candidate(chunk_id: str, document_id: str, score: float, rank: int) -> RetrievalCandidate:
    return RetrievalCandidate(
        chunk_id=chunk_id,
        document_id=document_id,
        content=f"content for {chunk_id}",
        scores=RetrievalScores(final_score=score),
        source=RetrievalSource.HYBRID,
        rank=rank,
    )


def persist_chunk(
    metadata_store: SQLiteMetadataStore,
    *,
    chunk_id: str,
    document_id: str,
    tags: list[str],
    document_type: str,
    trust_score: float,
    created_at: datetime,
) -> None:
    import asyncio

    asyncio.run(
        metadata_store.save_chunk(
            Chunk(
                id=chunk_id,
                document_id=document_id,
                content=f"content for {chunk_id}",
                location=ChunkLocation(start_char=0, end_char=10),
                sequence_number=0,
                metadata=ChunkMetadata(
                    document_title=document_id,
                    document_type=document_type,
                    tags=tags,
                    trust_score=trust_score,
                    section_title="Overview",
                    page_numbers=[1],
                ),
                created_at=created_at,
            )
        )
    )


def test_metadata_filter_restricts_by_document_id_and_tags(tmp_path) -> None:
    """Metadata filter should honor document and tag constraints."""
    metadata_store = SQLiteMetadataStore(db_path=str(tmp_path / "metadata.db"))
    now = datetime.now(timezone.utc)
    persist_chunk(metadata_store, chunk_id="chunk-001", document_id="doc-1", tags=["rag"], document_type="md", trust_score=0.9, created_at=now)
    persist_chunk(metadata_store, chunk_id="chunk-002", document_id="doc-2", tags=["security"], document_type="txt", trust_score=0.9, created_at=now)

    candidates = [make_candidate("chunk-001", "doc-1", 0.6, 0), make_candidate("chunk-002", "doc-2", 0.6, 1)]
    filtered = MetadataFilter(metadata_store).apply(
        candidates,
        FilterConfig(document_ids=["doc-1"], tags=["rag"]),
    )

    assert [candidate.chunk_id for candidate in filtered] == ["chunk-001"]


def test_freshness_booster_prefers_recent_chunks(tmp_path) -> None:
    """Freshness boosting should raise more recent content above older content."""
    metadata_store = SQLiteMetadataStore(db_path=str(tmp_path / "metadata.db"))
    now = datetime.now(timezone.utc)
    persist_chunk(metadata_store, chunk_id="chunk-new", document_id="doc-1", tags=["rag"], document_type="md", trust_score=0.9, created_at=now)
    persist_chunk(metadata_store, chunk_id="chunk-old", document_id="doc-2", tags=["rag"], document_type="md", trust_score=0.9, created_at=now - timedelta(days=120))

    boosted = FreshnessBooster(decay_days=30, max_boost=0.3).apply(
        [make_candidate("chunk-old", "doc-2", 0.5, 0), make_candidate("chunk-new", "doc-1", 0.5, 1)],
        metadata_store,
    )

    assert boosted[0].chunk_id == "chunk-new"


def test_trust_filter_blocks_low_trust_documents(tmp_path) -> None:
    """Trust filter should remove candidates under the configured trust floor."""
    metadata_store = SQLiteMetadataStore(db_path=str(tmp_path / "metadata.db"))
    now = datetime.now(timezone.utc)
    persist_chunk(metadata_store, chunk_id="chunk-hi1", document_id="doc-1", tags=["rag"], document_type="md", trust_score=0.95, created_at=now)
    persist_chunk(metadata_store, chunk_id="chunk-lo1", document_id="doc-2", tags=["rag"], document_type="md", trust_score=0.3, created_at=now)

    filtered = TrustFilter(metadata_store).apply(
        [make_candidate("chunk-hi1", "doc-1", 0.8, 0), make_candidate("chunk-lo1", "doc-2", 0.7, 1)],
        min_trust=0.8,
    )

    assert [candidate.chunk_id for candidate in filtered] == ["chunk-hi1"]
