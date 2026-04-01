"""Scope validation for routed queries."""

from __future__ import annotations

from src.layer1_contracts.schemas.security import SecurityDecision, SecurityDecisionType, ThreatCategory


class QueryScopeValidator:
    """Validate that a query is within configured operational scope."""

    def __init__(self, blocked_topics: list[str] | None = None, max_query_length: int = 10000) -> None:
        self.blocked_topics = blocked_topics or []
        self.max_query_length = max_query_length

    def validate(self, query_text: str) -> SecurityDecision:
        """Return whether the query is allowed to continue to routing."""
        if len(query_text) > self.max_query_length:
            return SecurityDecision(
                decision=SecurityDecisionType.DENY,
                threat_category=ThreatCategory.OVERSIZED,
                reason=f"Query exceeds max length of {self.max_query_length}",
            )

        text_lower = query_text.lower()
        for topic in self.blocked_topics:
            if topic.lower() in text_lower:
                return SecurityDecision(
                    decision=SecurityDecisionType.DENY,
                    threat_category=ThreatCategory.FORBIDDEN_CONTENT,
                    reason="Query contains blocked topic",
                )

        return SecurityDecision(decision=SecurityDecisionType.ALLOW, threat_category=ThreatCategory.NONE)
