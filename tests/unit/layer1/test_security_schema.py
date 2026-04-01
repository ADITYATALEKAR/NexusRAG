"""Tests for security schemas."""

import pytest
from pydantic import ValidationError

from src.layer1_contracts.schemas.security import SecurityDecision, SecurityDecisionType


def test_security_decision_defaults_are_safe() -> None:
    """Security decision defaults should be sensible."""
    decision = SecurityDecision(decision=SecurityDecisionType.ALLOW)

    assert decision.sanitized is False
    assert decision.modifications == []


def test_security_schema_forbids_extra_fields() -> None:
    """Unexpected security fields should be rejected."""
    with pytest.raises(ValidationError):
        SecurityDecision(decision=SecurityDecisionType.ALLOW, extra_field="nope")
