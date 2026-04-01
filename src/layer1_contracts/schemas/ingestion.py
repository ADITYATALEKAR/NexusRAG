"""Ingestion contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IngestionStatus(str, Enum):
    """Ingestion lifecycle states."""

    PENDING = "pending"
    VALIDATING = "validating"
    PARSING = "parsing"
    NORMALIZING = "normalizing"
    PREPARING_CHUNKS = "preparing_chunks"
    COMPLETED = "completed"
    FAILED = "failed"


class FileMetadata(BaseModel):
    """Input file metadata."""

    model_config = ConfigDict(extra="forbid")

    filename: str
    file_size_bytes: int
    mime_type: str | None = None
    extension: str
    created_at: datetime | None = None
    modified_at: datetime | None = None


class IngestionRequest(BaseModel):
    """Request to ingest a file."""

    model_config = ConfigDict(extra="forbid")

    id: str
    file_path: str
    file_metadata: FileMetadata
    options: dict[str, Any] = Field(default_factory=dict)
    request_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IngestionResult(BaseModel):
    """Result of an ingestion attempt."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    document_id: str
    status: IngestionStatus
    parser_used: str
    parser_confidence: float = Field(ge=0.0, le=1.0)
    page_count: int | None = None
    word_count: int | None = None
    chunk_count: int = 0
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    processing_time_ms: int
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
