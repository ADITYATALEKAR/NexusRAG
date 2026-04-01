"""Rule-based query router."""

from __future__ import annotations

from datetime import datetime, timezone

from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.query_understanding import QueryAnalysis
from src.layer1_contracts.schemas.routing import Route, RouteType, RoutingDecision
from src.layer2_domain.query_understanding.classifier import QueryClassifier
from src.layer2_domain.routing.confidence_scorer import RoutingConfidenceScorer
from src.layer2_domain.routing.route_selector import RouteSelector


class QueryRouter:
    """Route queries to the most appropriate bounded execution strategy."""

    def __init__(
        self,
        classifier: QueryClassifier,
        confidence_scorer: RoutingConfidenceScorer | None = None,
        route_selector: RouteSelector | None = None,
        confidence_threshold: float = 0.6,
        enable_structured: bool = True,
        enable_decomposition: bool = True,
        max_decomposition_hops: int = 2,
        route_configs: dict[str, dict[str, object]] | None = None,
        default_fallback_route: RouteType = RouteType.STANDARD,
    ) -> None:
        self.classifier = classifier
        self.confidence_scorer = confidence_scorer or RoutingConfidenceScorer()
        self.route_selector = route_selector or RouteSelector()
        self.confidence_threshold = confidence_threshold
        self.enable_structured = enable_structured
        self.enable_decomposition = enable_decomposition
        self.max_decomposition_hops = max(1, max_decomposition_hops)
        self.route_configs = route_configs or {}
        self.default_fallback_route = default_fallback_route
        self._last_scores: dict[str, dict[str, float]] = {}

    def route(self, query: Query) -> RoutingDecision:
        """Analyze the query and return the best route with alternatives."""
        start = datetime.now(timezone.utc)
        analysis = self.classifier.classify(query.text)
        analysis = analysis.model_copy(update={"query_id": query.id})
        route_scores = self._apply_runtime_constraints(self.confidence_scorer.score_routes(analysis))
        sorted_routes = self.route_selector.select(route_scores)
        best_route_type, best_score = sorted_routes[0]
        fallback_route = self._get_fallback(best_route_type)
        selected_route = Route(
            route_type=best_route_type,
            confidence=best_score,
            reasoning=self._generate_reasoning(analysis, best_route_type),
            fallback_route=fallback_route,
            parameters=self._get_route_parameters(analysis, best_route_type),
        )
        alternatives = [
            Route(
                route_type=route_type,
                confidence=score,
                reasoning=f"Alternative: {route_type.value}",
                fallback_route=RouteType.STANDARD,
            )
            for route_type, score in sorted_routes[1:3]
        ]
        elapsed = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
        self._last_scores[query.id] = {route_type.value: score for route_type, score in sorted_routes}
        return RoutingDecision(
            query_id=query.id,
            selected_route=selected_route,
            alternative_routes=alternatives,
            query_analysis=analysis,
            routing_time_ms=elapsed,
        )

    def get_scores(self, query_id: str) -> dict[str, float]:
        """Return the most recent route scores for a query id."""
        return self._last_scores.get(query_id, {})

    def _get_fallback(self, route_type: RouteType) -> RouteType:
        fallbacks = {
            RouteType.STRUCTURED: self.default_fallback_route,
            RouteType.COMPARATIVE: self.default_fallback_route,
            RouteType.TWO_HOP: self.default_fallback_route,
            RouteType.KEYWORD_HEAVY: self.default_fallback_route,
            RouteType.SEMANTIC_HEAVY: self.default_fallback_route,
            RouteType.DIRECT_ANSWER: self.default_fallback_route,
        }
        return fallbacks.get(route_type, self.default_fallback_route)

    def _generate_reasoning(self, analysis: QueryAnalysis, route: RouteType) -> str:
        return (
            f"Selected {route.value} based on query_type={analysis.query_type.value}, "
            f"intent={analysis.intent.value}, complexity={analysis.complexity.value}"
        )

    def _get_route_parameters(self, analysis: QueryAnalysis, route: RouteType) -> dict[str, object]:
        params: dict[str, object] = dict(self.route_configs.get(route.value, {}))
        if route == RouteType.KEYWORD_HEAVY:
            params.setdefault("lexical_weight", 0.7)
            params.setdefault("dense_weight", 0.3)
        elif route == RouteType.SEMANTIC_HEAVY:
            params.setdefault("lexical_weight", 0.3)
            params.setdefault("dense_weight", 0.7)
        elif route == RouteType.COMPARATIVE:
            max_sub_queries = int(params.get("max_sub_queries", len(analysis.sub_queries) or 3))
            params["sub_queries"] = analysis.sub_queries[:max_sub_queries]
            params["max_sub_queries"] = max_sub_queries
        elif route == RouteType.TWO_HOP:
            configured_max_hops = int(params.get("max_hops", self.max_decomposition_hops))
            params["max_hops"] = min(configured_max_hops, self.max_decomposition_hops)
        elif route == RouteType.STRUCTURED:
            params["requires_structured"] = analysis.requires_structured
        return params

    def _apply_runtime_constraints(self, scores: dict[RouteType, float]) -> dict[RouteType, float]:
        """Apply config-driven feature flags and hop limits to route scores."""
        constrained: dict[RouteType, float] = dict(scores)
        if not self.enable_structured:
            constrained[RouteType.STRUCTURED] = 0.0
        if not self.enable_decomposition:
            constrained[RouteType.COMPARATIVE] = 0.0
            constrained[RouteType.TWO_HOP] = 0.0
        elif self.max_decomposition_hops < 2:
            constrained[RouteType.TWO_HOP] = 0.0
        constrained[RouteType.STANDARD] = max(constrained.get(RouteType.STANDARD, 0.0), 0.5)
        return {route_type: float(score) for route_type, score in constrained.items()}
