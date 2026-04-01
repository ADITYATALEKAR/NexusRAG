"""Query understanding contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from src.layer1_contracts.schemas.query import QueryType


class QueryIntent(str, Enum):
    """High-level intent detected in a query."""

    FACTUAL = "factual"
    EXPLANATORY = "explanatory"
    COMPARATIVE = "comparative"
    PROCEDURAL = "procedural"
    ANALYTICAL = "analytical"
    AGGREGATION = "aggregation"
    TEMPORAL = "temporal"
    UNKNOWN = "unknown"


class QueryComplexity(str, Enum):
    """Complexity estimate used by the router."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    STRUCTURED = "structured"


class DetectedEntity(BaseModel):
    """A lightweight entity mention detected in the query."""

    model_config = ConfigDict(extra="forbid")

    text: str
    entity_type: str
    start: int
    end: int
    confidence: float = Field(ge=0.0, le=1.0)


class QueryAnalysis(BaseModel):
    """Normalized routing-oriented analysis of one query."""

    model_config = ConfigDict(extra="forbid")

    query_id: str
    original_text: str
    cleaned_text: str
    query_type: QueryType
    intent: QueryIntent
    complexity: QueryComplexity
    entities: list[DetectedEntity] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    requires_structured: bool = False
    requires_decomposition: bool = False
    sub_queries: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    analysis_time_ms: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
