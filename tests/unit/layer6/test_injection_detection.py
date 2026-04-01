"""Tests for injection detection."""

from src.layer1_contracts.schemas.security import SecurityDecisionType, ThreatCategory
from src.layer6_security.input.injection_detection import InjectionDetector


def test_detector_blocks_sql_injection_patterns() -> None:
    """Basic SQL injection strings should be denied."""
    detector = InjectionDetector()
    decision = detector.detect("select * from x union select password from users")

    assert decision.decision == SecurityDecisionType.DENY
    assert decision.threat_category == ThreatCategory.INJECTION
