"""Route ranking helpers."""

from __future__ import annotations

from src.layer1_contracts.schemas.routing import RouteType


class RouteSelector:
    """Rank route candidates with a deterministic tie-break order."""

    PREFERENCE_ORDER = {
        RouteType.STRUCTURED: 0,
        RouteType.COMPARATIVE: 1,
        RouteType.TWO_HOP: 2,
        RouteType.KEYWORD_HEAVY: 3,
        RouteType.SEMANTIC_HEAVY: 4,
        RouteType.STANDARD: 5,
        RouteType.DIRECT_ANSWER: 6,
    }

    def select(self, scores: dict[RouteType, float]) -> list[tuple[RouteType, float]]:
        """Return routes ordered by descending score and stable preference."""
        return sorted(
            scores.items(),
            key=lambda item: (-item[1], self.PREFERENCE_ORDER.get(item[0], 999)),
        )
