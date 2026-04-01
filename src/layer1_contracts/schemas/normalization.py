"""Normalization contracts."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field

from src.layer1_contracts.schemas.document import DocumentMetadata


class NormalizedSection(BaseModel):
    """Normalized section ready for chunk preparation."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str | None = None
    level: int
    content: str
    content_type: str = "text"
    start_char: int
    end_char: int
    page_numbers: list[int] = Field(default_factory=list)
    parent_id: str | None = None
    children_ids: list[str] = Field(default_factory=list)


class NormalizedDocument(BaseModel):
    """Canonical normalized document ready for chunking."""

    model_config = ConfigDict(extra="forbid")

    id: str
    original_document_id: str
    content: str
    sections: list[NormalizedSection] = Field(default_factory=list)
    tables: list[dict] = Field(default_factory=list)
    code_blocks: list[dict] = Field(default_factory=list)
    lists: list[dict] = Field(default_factory=list)
    metadata: DocumentMetadata
    page_count: int
    word_count: int
    char_count: int
    normalized_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChunkPrecursor(BaseModel):
    """Pre-chunk unit with boundary metadata."""

    model_config = ConfigDict(extra="forbid")

    id: str
    document_id: str
    content: str
    section_id: str | None = None
    section_title: str | None = None
    section_hierarchy: list[str] = Field(default_factory=list)
    content_type: str = "text"
    start_char: int
    end_char: int
    page_numbers: list[int] = Field(default_factory=list)
    suggested_split_points: list[int] = Field(default_factory=list)
    is_complete_section: bool = False
