"""Query injection protection for routed execution."""

from __future__ import annotations

import re

from src.layer1_contracts.schemas.security import SecurityDecision, SecurityDecisionType, ThreatCategory


class QueryInjectionGuard:
    """Enhanced injection detection for routing-aware query execution."""

    PROMPT_INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior|above)",
        r"disregard\s+(all\s+)?instructions",
        r"forget\s+(everything|all)",
        r"you\s+are\s+now\s+",
        r"new\s+instructions?:",
        r"system\s*prompt",
        r"</?(system|user|assistant)>",
        r"\[INST\]|\[/INST\]",
        r"human:|assistant:",
    ]
    SQL_INJECTION_PATTERNS = [
        r"'\s*OR\s+'1'\s*=\s*'1",
        r";\s*(DROP|DELETE|UPDATE|INSERT)",
        r"UNION\s+(ALL\s+)?SELECT",
        r"--\s*$",
        r"/\*.*\*/",
    ]

    def check(self, query_text: str) -> SecurityDecision:
        """Return the security decision for a query before routing starts."""
        text_lower = query_text.lower()
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text_lower):
                return SecurityDecision(
                    decision=SecurityDecisionType.DENY,
                    threat_category=ThreatCategory.PROMPT_INJECTION,
                    reason="Potential prompt injection detected",
                    rule_triggered=pattern[:30],
                )
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, query_text, re.IGNORECASE):
                return SecurityDecision(
                    decision=SecurityDecisionType.DENY,
                    threat_category=ThreatCategory.INJECTION,
                    reason="Potential SQL injection detected",
                    rule_triggered=pattern[:30],
                )
        return SecurityDecision(decision=SecurityDecisionType.ALLOW, threat_category=ThreatCategory.NONE)
