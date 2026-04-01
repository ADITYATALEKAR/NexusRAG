"""Generation contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from src.layer1_contracts.schemas.evidence import EvidenceBundle
from src.layer1_contracts.schemas.query import Query


class GenerationConfig(BaseModel):
    """Configuration for one generation request."""

    model_config = ConfigDict(extra="forbid")

    model: str | None = None
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_output_tokens: int = Field(default=1024, ge=1, le=8000)
    require_citations: bool = True
    allow_abstention: bool = True
    grounding_threshold: float = Field(default=0.5, ge=0.0, le=1.0)


class GenerationRequest(BaseModel):
    """Request for answer generation."""

    model_config = ConfigDict(extra="forbid")

    id: str
    query: Query
    evidence_bundle: EvidenceBundle
    config: GenerationConfig = Field(default_factory=GenerationConfig)
    system_prompt_override: str | None = None
    request_id: str | None = None


class GenerationTrace(BaseModel):
    """Trace metadata for one generation run."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    request_id: str
    query_text: str
    evidence_items: list[str]
    prompt_tokens: int
    completion_tokens: int
    provider_used: str
    model_used: str
    fallback_occurred: bool
    fallback_chain: list[str]
    latency_ms: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AbstentionReason(str, Enum):
    """Reasons for abstaining from an answer."""

    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    LOW_CONFIDENCE = "low_confidence"
    OUT_OF_SCOPE = "out_of_scope"
    CONFLICTING_EVIDENCE = "conflicting_evidence"
    SAFETY_FILTER = "safety_filter"
