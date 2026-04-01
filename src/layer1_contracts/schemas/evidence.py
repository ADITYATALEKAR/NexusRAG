"""Evidence contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class EvidenceSelectionStrategy(str, Enum):
    """Evidence item selection strategies."""

    TOP_K = "top_k"
    MMR = "mmr"
    DIVERSITY = "diversity"


class EvidenceConfig(BaseModel):
    """Configuration for evidence assembly."""

    model_config = ConfigDict(extra="forbid")

    max_evidence_items: int = Field(default=5, ge=1, le=20)
    max_total_tokens: int = Field(default=3000, ge=500, le=100000)
    min_relevance_score: float = Field(default=0.3, ge=0.0, le=1.0)
    selection_strategy: EvidenceSelectionStrategy = EvidenceSelectionStrategy.TOP_K
    preserve_order: bool = True
    include_source_context: bool = True


class EvidenceItem(BaseModel):
    """One selected evidence item."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    document_id: str
    content: str
    citation_key: str
    document_title: str | None = None
    section_title: str | None = None
    page_numbers: list[int] = Field(default_factory=list)
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    token_count: int | None = None
    was_truncated: bool = False


class EvidenceBundle(BaseModel):
    """Selected evidence set."""

    model_config = ConfigDict(extra="forbid")

    query_id: str
    items: list[EvidenceItem] = Field(default_factory=list)
    total_candidates_considered: int = 0
    selection_strategy: str = "top_k"
    total_tokens: int = 0
    max_tokens_allowed: int = 4000
    min_relevance_score: float | None = None
    max_relevance_score: float | None = None
    avg_relevance_score: float | None = None
    assembled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvidenceAssemblyResult(BaseModel):
    """Result of evidence assembly."""

    model_config = ConfigDict(extra="forbid")

    bundle: EvidenceBundle
    total_tokens: int
    items_selected: int
    items_truncated: int
    items_dropped: int
    assembly_time_ms: int
