"""Route confidence scoring."""

from __future__ import annotations

from src.layer1_contracts.schemas.query import QueryType
from src.layer1_contracts.schemas.query_understanding import QueryAnalysis, QueryComplexity, QueryIntent
from src.layer1_contracts.schemas.routing import RouteType


class RoutingConfidenceScorer:
    """Score candidate route types for a classified query."""

    def score_routes(self, analysis: QueryAnalysis) -> dict[RouteType, float]:
        """Return bounded route scores for the given analysis."""
        scores = {route_type: 0.0 for route_type in RouteType}
        type_to_route = {
            QueryType.KEYWORD: RouteType.KEYWORD_HEAVY,
            QueryType.SEMANTIC: RouteType.SEMANTIC_HEAVY,
            QueryType.HYBRID: RouteType.STANDARD,
            QueryType.STRUCTURED: RouteType.STRUCTURED,
            QueryType.COMPARATIVE: RouteType.COMPARATIVE,
            QueryType.MULTI_HOP: RouteType.TWO_HOP,
        }

        mapped_route = type_to_route.get(analysis.query_type)
        if mapped_route is not None:
            scores[mapped_route] = max(scores[mapped_route], analysis.confidence)

        scores[RouteType.STANDARD] = max(scores[RouteType.STANDARD], 0.5)

        if analysis.query_type == QueryType.HYBRID and analysis.intent in {
            QueryIntent.EXPLANATORY,
            QueryIntent.ANALYTICAL,
        }:
            scores[RouteType.SEMANTIC_HEAVY] = max(scores[RouteType.SEMANTIC_HEAVY], 0.68)

        if analysis.query_type == QueryType.HYBRID and any(keyword.isdigit() or keyword.isupper() for keyword in analysis.keywords):
            scores[RouteType.KEYWORD_HEAVY] = max(scores[RouteType.KEYWORD_HEAVY], 0.66)

        if analysis.complexity == QueryComplexity.SIMPLE:
            scores[RouteType.STANDARD] += 0.1
            scores[RouteType.DIRECT_ANSWER] += 0.1
        elif analysis.complexity == QueryComplexity.COMPLEX:
            scores[RouteType.TWO_HOP] += 0.1
        elif analysis.complexity == QueryComplexity.STRUCTURED:
            scores[RouteType.STRUCTURED] += 0.1

        if analysis.intent == QueryIntent.AGGREGATION:
            scores[RouteType.STRUCTURED] += 0.15
        if analysis.intent == QueryIntent.COMPARATIVE:
            scores[RouteType.COMPARATIVE] += 0.15

        return {route_type: min(max(score, 0.0), 1.0) for route_type, score in scores.items()}
