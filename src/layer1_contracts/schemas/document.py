"""Document contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.layer0_core.constants.patterns import IDENTIFIER_PATTERN


class DocumentType(str, Enum):
    """Supported document formats."""

    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"
    CSV = "csv"
    JSON = "json"
    UNKNOWN = "unknown"


class DocumentStatus(str, Enum):
    """Document lifecycle states."""

    PENDING = "pending"
    VALIDATING = "validating"
    PARSING = "parsing"
    PARSED = "parsed"
    NORMALIZED = "normalized"
    CHUNKED = "chunked"
    INDEXED = "indexed"
    FAILED = "failed"


class DocumentMetadata(BaseModel):
    """Document metadata."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    author: str | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None
    source_url: str | None = None
    page_count: int | None = None
    word_count: int | None = None
    char_count: int | None = None
    mime_type: str | None = None
    tags: list[str] = Field(default_factory=list)
    custom: dict[str, Any] = Field(default_factory=dict)


class Document(BaseModel):
    """Document contract."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=8, max_length=64)
    content: str
    document_type: DocumentType
    status: DocumentStatus = DocumentStatus.PENDING
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    checksum: str | None = None
    parser_used: str | None = None
    parser_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    original_size_bytes: int | None = Field(default=None, ge=0)
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        """Validate identifier formatting."""
        if not re.match(IDENTIFIER_PATTERN, value):
            raise ValueError("ID must be alphanumeric with hyphens/underscores")
        return value
