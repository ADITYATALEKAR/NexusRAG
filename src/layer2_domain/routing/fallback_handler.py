"""Fallback handling for routed query execution."""

from __future__ import annotations

from typing import Any, Protocol

from src.layer1_contracts.schemas.answer import Answer
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.retrieval_config import RetrievalConfig, RetrievalMode
from src.layer1_contracts.schemas.routing import Route, RouteType


class StandardRouteExecutor(Protocol):
    """Protocol for the bounded standard answer path used during fallback."""

    async def execute(
        self,
        query: Query,
        retrieval_config: RetrievalConfig | None = None,
        evidence_config: Any = None,
        generation_config: Any = None,
    ) -> tuple[Answer, Any]:
        """Execute the standard query path and return an answer tuple."""


class FallbackHandler:
    """Decide when routed execution should fall back to a simpler path."""

    def __init__(
        self,
        confidence_threshold: float = 0.5,
        low_quality_threshold: float = 0.3,
        fallback_route: RouteType = RouteType.STANDARD,
        trigger_on_low_confidence: bool = True,
        trigger_on_error: bool = True,
    ) -> None:
        self.confidence_threshold = confidence_threshold
        self.low_quality_threshold = low_quality_threshold
        self.fallback_route = fallback_route
        self.trigger_on_low_confidence = trigger_on_low_confidence
        self.trigger_on_error = trigger_on_error

    def should_fallback(
        self,
        route: Route,
        result_quality: float | None = None,
    ) -> tuple[bool, str]:
        """Return whether the route should fall back and the reason."""
        if self.trigger_on_low_confidence and route.confidence < self.confidence_threshold:
            return True, f"Route confidence {route.confidence:.2f} below threshold"
        if result_quality is not None and result_quality < self.low_quality_threshold:
            return True, f"Result quality {result_quality:.2f} too low"
        return False, ""

    def resolve_route(self, route: Route) -> RouteType:
        """Return the fallback route type for the given route."""
        return route.fallback_route or self.fallback_route

    async def execute_fallback(
        self,
        original_route: Route,
        query: Query,
        standard_executor: StandardRouteExecutor,
    ) -> tuple[Answer, RouteType]:
        """Execute the configured fallback path through the bounded standard flow."""
        fallback_route = self.resolve_route(original_route)
        retrieval_config = None
        if fallback_route == RouteType.STANDARD:
            retrieval_config = RetrievalConfig(mode=RetrievalMode.HYBRID)
        answer, _ = await standard_executor.execute(query, retrieval_config=retrieval_config)
        return answer, fallback_route
