"""Structured retrieval contracts."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StructuredQueryType(str, Enum):
    """Supported structured query shapes."""

    LOOKUP = "lookup"
    AGGREGATION = "aggregation"
    FILTER = "filter"
    COMPARISON = "comparison"
    RANKING = "ranking"


class StructuredQuery(BaseModel):
    """Normalized structured query plan."""

    model_config = ConfigDict(extra="forbid")

    id: str
    natural_query: str
    query_type: StructuredQueryType
    target_table: str
    columns: list[str] = Field(default_factory=list)
    filters: dict[str, object] = Field(default_factory=dict)
    aggregations: list[str] = Field(default_factory=list)
    order_by: str | None = None
    limit: int | None = None


class GeneratedSQL(BaseModel):
    """Safe SQL emitted for a structured query."""

    model_config = ConfigDict(extra="forbid")

    query_id: str
    sql: str
    template_used: str
    parameters: dict[str, object] = Field(default_factory=dict)
    is_safe: bool = True
    safety_warnings: list[str] = Field(default_factory=list)


class StructuredResult(BaseModel):
    """Execution result for a structured query."""

    model_config = ConfigDict(extra="forbid")

    query_id: str
    rows: list[dict[str, object]]
    columns: list[str]
    row_count: int
    execution_time_ms: int
    formatted_answer: str | None = None
