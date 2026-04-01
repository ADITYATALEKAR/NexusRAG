"""Intent detection for routed queries."""

from __future__ import annotations

from src.layer1_contracts.schemas.query_understanding import QueryIntent


class IntentDetector:
    """Infer a coarse-grained user intent from the query text."""

    def detect(self, text: str) -> QueryIntent:
        """Return the most likely intent for the supplied text."""
        text_lower = text.lower()

        if any(token in text_lower for token in ["how to", "how do i", "steps to", "guide"]):
            return QueryIntent.PROCEDURAL
        if any(token in text_lower for token in ["what is", "define", "explain", "meaning of", "overview"]):
            return QueryIntent.EXPLANATORY
        if any(token in text_lower for token in ["compare", "difference", "vs", "versus", "better"]):
            return QueryIntent.COMPARATIVE
        if any(token in text_lower for token in ["total", "sum", "count", "average", "how many", "how much"]):
            return QueryIntent.AGGREGATION
        if any(token in text_lower for token in ["when", "what year", "what date", "timeline"]):
            return QueryIntent.TEMPORAL
        if any(token in text_lower for token in ["why", "analyze", "impact", "effect", "tradeoff"]):
            return QueryIntent.ANALYTICAL
        return QueryIntent.FACTUAL
