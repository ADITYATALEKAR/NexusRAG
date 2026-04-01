"""Chunk contracts."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ChunkLocation(BaseModel):
    """Chunk span information."""

    model_config = ConfigDict(extra="forbid")

    start_char: int = Field(..., ge=0)
    end_char: int = Field(..., ge=0)
    start_page: int | None = Field(None, ge=1)
    end_page: int | None = Field(None, ge=1)

    @model_validator(mode="after")
    def validate_offsets(self) -> "ChunkLocation":
        """Ensure the location is coherent."""
        if self.end_char < self.start_char:
            raise ValueError("end_char must be greater than or equal to start_char")
        if self.start_page and self.end_page and self.end_page < self.start_page:
            raise ValueError("end_page must be greater than or equal to start_page")
        return self


class ChunkMetadata(BaseModel):
    """Chunk metadata."""

    model_config = ConfigDict(extra="forbid")

    document_title: str | None = None
    document_type: str | None = None
    tags: list[str] = Field(default_factory=list)
    trust_score: float | None = Field(default=None, ge=0.0, le=1.0)
    section_title: str | None = None
    section_hierarchy: list[str] = Field(default_factory=list)
    page_numbers: list[int] = Field(default_factory=list)
    is_table: bool = False
    is_code: bool = False


class Chunk(BaseModel):
    """Chunk contract."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=8, max_length=64)
    document_id: str
    content: str = Field(..., min_length=1)
    location: ChunkLocation
    sequence_number: int = Field(..., ge=0)
    parent_chunk_id: str | None = None
    child_chunk_ids: list[str] = Field(default_factory=list)
    metadata: ChunkMetadata = Field(default_factory=ChunkMetadata)
    token_count: int | None = Field(None, ge=0)
    embedding: list[float] | None = None
    embedding_model: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
