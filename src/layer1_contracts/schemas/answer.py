"""Answer contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class AnswerStatus(str, Enum):
    """Answer generation outcomes."""

    SUCCESS = "success"
    PARTIAL = "partial"
    ABSTAINED = "abstained"
    FAILED = "failed"
    FILTERED = "filtered"


class Citation(BaseModel):
    """Citation metadata."""

    model_config = ConfigDict(extra="forbid")

    citation_key: str
    chunk_id: str
    document_id: str
    document_title: str | None = None
    page_numbers: list[int] = Field(default_factory=list)
    quoted_text: str | None = None


class AnswerMetadata(BaseModel):
    """Answer generation metadata."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    model_used: str
    provider_used: str
    fallback_occurred: bool = False
    fallback_chain: list[str] = Field(default_factory=list)
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    generation_latency_ms: int | None = None


class Answer(BaseModel):
    """Answer contract."""

    model_config = ConfigDict(extra="forbid")

    id: str
    query_id: str
    text: str
    status: AnswerStatus
    citations: list[Citation] = Field(default_factory=list)
    evidence_bundle_id: str | None = None
    evidence_item_ids: list[str] = Field(default_factory=list)
    safety_filtered: bool = False
    safety_filter_reason: str | None = None
    metadata: AnswerMetadata
    abstention_reason: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
