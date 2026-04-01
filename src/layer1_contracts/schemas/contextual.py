"""Contextual indexing contracts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ContextualChunk(BaseModel):
    """Chunk content enriched with document-level context."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    original_content: str
    contextual_content: str
    context_source: str
    context_tokens: int = Field(ge=0)


class DocumentContext(BaseModel):
    """Structured context generated for one document."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    summary: str
    key_topics: list[str] = Field(default_factory=list)
