"""Routing contracts."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from src.layer1_contracts.schemas.query_understanding import QueryAnalysis


class RouteType(str, Enum):
    """Supported Phase 5 route strategies."""

    STANDARD = "standard"
    KEYWORD_HEAVY = "keyword_heavy"
    SEMANTIC_HEAVY = "semantic_heavy"
    STRUCTURED = "structured"
    COMPARATIVE = "comparative"
    TWO_HOP = "two_hop"
    DIRECT_ANSWER = "direct_answer"


class Route(BaseModel):
    """A concrete routing decision."""

    model_config = ConfigDict(extra="forbid")

    route_type: RouteType
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    fallback_route: RouteType | None = RouteType.STANDARD
    parameters: dict[str, object] = Field(default_factory=dict)


class RoutingDecision(BaseModel):
    """Router output including alternatives."""

    model_config = ConfigDict(extra="forbid")

    query_id: str
    selected_route: Route
    alternative_routes: list[Route] = Field(default_factory=list)
    query_analysis: QueryAnalysis
    routing_time_ms: int


class RoutingDiagnostics(BaseModel):
    """Execution-time routing metadata surfaced by the API."""

    model_config = ConfigDict(extra="forbid")

    query_id: str
    selected_route: RouteType
    route_confidence: float
    classifier_scores: dict[str, float]
    fallback_triggered: bool = False
    fallback_reason: str | None = None
    final_route_used: RouteType
