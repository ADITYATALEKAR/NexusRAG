"""Tests for input validation."""

from src.layer1_contracts.schemas.security import SecurityDecisionType, ThreatCategory
from src.layer6_security.input.validation import InputValidator


def test_validator_rejects_oversized_query() -> None:
    """Queries over the configured max should be denied."""
    validator = InputValidator(max_query_length=5)
    decision = validator.validate_query("too long")

    assert decision.decision == SecurityDecisionType.DENY
    assert decision.threat_category == ThreatCategory.OVERSIZED
