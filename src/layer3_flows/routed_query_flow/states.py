"""States for routed query execution."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.layer1_contracts.schemas.answer import Answer
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.routing import RouteType, RoutingDecision, RoutingDiagnostics


class RoutedQueryState(str, Enum):
    """Execution states for Phase 5 routed queries."""

    SECURITY_CHECK = "security_check"
    ROUTING = "routing"
    EXECUTING = "executing"
    FALLBACK = "fallback"
    FILTERED = "filtered"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True)
class RoutedQueryContext:
    """Mutable context carried through routed execution."""

    query: Query
    forced_route: RouteType | None = None
    state: RoutedQueryState = RoutedQueryState.SECURITY_CHECK
    routing_decision: RoutingDecision | None = None
    answer: Answer | None = None
    diagnostics: RoutingDiagnostics | None = None
    error: str | None = None
