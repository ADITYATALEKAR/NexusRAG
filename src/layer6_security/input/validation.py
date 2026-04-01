"""Input validation."""

from __future__ import annotations

from src.layer0_core.constants.limits import MAX_DOCUMENT_SIZE_BYTES, MAX_QUERY_LENGTH
from src.layer1_contracts.schemas.security import SecurityDecision, SecurityDecisionType, ThreatCategory


class InputValidator:
    """Validate basic input constraints."""

    def __init__(
        self,
        max_query_length: int = MAX_QUERY_LENGTH,
        max_document_size_bytes: int = MAX_DOCUMENT_SIZE_BYTES,
    ) -> None:
        self.max_query_length = max_query_length
        self.max_document_size_bytes = max_document_size_bytes

    def validate_query(self, query: str) -> SecurityDecision:
        """Validate query size and shape."""
        if not query.strip():
            return SecurityDecision(
                decision=SecurityDecisionType.DENY,
                threat_category=ThreatCategory.MALFORMED,
                reason="Query must not be empty",
                rule_triggered="query_non_empty",
            )
        if len(query) > self.max_query_length:
            return SecurityDecision(
                decision=SecurityDecisionType.DENY,
                threat_category=ThreatCategory.OVERSIZED,
                reason=f"Query exceeds max length of {self.max_query_length}",
                rule_triggered="query_max_length",
            )
        return SecurityDecision(decision=SecurityDecisionType.ALLOW)

    def validate_document_size(self, size_bytes: int) -> SecurityDecision:
        """Validate document size."""
        if size_bytes > self.max_document_size_bytes:
            return SecurityDecision(
                decision=SecurityDecisionType.DENY,
                threat_category=ThreatCategory.OVERSIZED,
                reason=f"Document exceeds max size of {self.max_document_size_bytes} bytes",
                rule_triggered="document_max_size",
            )
        return SecurityDecision(decision=SecurityDecisionType.ALLOW)
