"""Indexing contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class IndexStatus(str, Enum):
    """Index job lifecycle states."""

    PENDING = "pending"
    EMBEDDING = "embedding"
    VECTOR_INDEXING = "vector_indexing"
    LEXICAL_INDEXING = "lexical_indexing"
    COMPLETED = "completed"
    FAILED = "failed"
    STALE = "stale"


class IndexJob(BaseModel):
    """An indexing job for one document."""

    model_config = ConfigDict(extra="forbid")

    id: str
    document_id: str
    chunk_ids: list[str]
    status: IndexStatus = IndexStatus.PENDING
    vector_store_id: str | None = None
    lexical_store_id: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    completed_at: datetime | None = None


class IndexState(BaseModel):
    """Tracks index state for a document."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    document_checksum: str
    indexed_at: datetime
    chunk_count: int
    embedding_model: str
    is_stale: bool = False
    last_verified_at: datetime | None = None


class IndexingResult(BaseModel):
    """Result of indexing chunks into storage backends."""

    model_config = ConfigDict(extra="forbid")

    job_id: str
    document_id: str
    status: IndexStatus
    chunks_indexed: int
    vector_index_time_ms: int
    lexical_index_time_ms: int
    total_time_ms: int
    errors: list[str] = Field(default_factory=list)
