"""Baseline injection detection."""

from __future__ import annotations

import re

from src.layer1_contracts.schemas.security import SecurityDecision, SecurityDecisionType, ThreatCategory


class InjectionDetector:
    """Detect SQL injection and prompt injection patterns."""

    DEFAULT_PATTERNS = [
        (re.compile(r"(?i)\b(union\s+select|drop\s+table|delete\s+from)\b"), ThreatCategory.INJECTION),
        (
            re.compile(r"(?i)(ignore\s+previous\s+instructions|forget\s+the\s+rules|system\s+prompt:)"),
            ThreatCategory.PROMPT_INJECTION,
        ),
    ]

    def __init__(self, patterns=None) -> None:
        self.patterns = patterns or self.DEFAULT_PATTERNS

    def detect(self, text: str) -> SecurityDecision:
        """Return a security decision for the input text."""
        for pattern, category in self.patterns:
            if pattern.search(text):
                return SecurityDecision(
                    decision=SecurityDecisionType.DENY,
                    threat_category=category,
                    reason=f"Matched dangerous pattern: {pattern.pattern}",
                    rule_triggered=pattern.pattern,
                )
        return SecurityDecision(decision=SecurityDecisionType.ALLOW)
