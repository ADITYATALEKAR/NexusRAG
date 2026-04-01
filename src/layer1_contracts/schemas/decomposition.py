"""Decomposition contracts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SubQuery(BaseModel):
    """One bounded sub-query in a decomposition plan."""

    model_config = ConfigDict(extra="forbid")

    id: str
    text: str
    purpose: str
    depends_on: list[str] = Field(default_factory=list)
    order: int


class DecompositionPlan(BaseModel):
    """Plan for bounded multi-step retrieval."""

    model_config = ConfigDict(extra="forbid")

    original_query_id: str
    original_text: str
    sub_queries: list[SubQuery]
    strategy: str
    max_hops: int = 2


class SubQueryResult(BaseModel):
    """One executed sub-query result."""

    model_config = ConfigDict(extra="forbid")

    sub_query_id: str
    answer: str
    evidence_used: list[str]
    confidence: float = Field(ge=0.0, le=1.0)


class AggregatedAnswer(BaseModel):
    """Synthesis of bounded sub-query results."""

    model_config = ConfigDict(extra="forbid")

    original_query_id: str
    final_answer: str
    sub_results: list[SubQueryResult]
    synthesis_strategy: str
    total_evidence: list[str]
