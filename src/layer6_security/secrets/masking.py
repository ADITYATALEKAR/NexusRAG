"""Secret masking."""

from __future__ import annotations

import re


class SecretMasker:
    """Mask secrets in logs and error messages."""

    MASK = "***REDACTED***"

    DEFAULT_PATTERNS = [
        re.compile(
            r'(api[_-]?key|apikey|secret[_-]?key|password|token|bearer|authorization|credential)'
            r'["\']?\s*[:=]\s*["\']?([^"\'\s,}]{8,})',
            re.IGNORECASE,
        ),
        re.compile(r"sk-[a-zA-Z0-9\-_]{20,}"),
        re.compile(r"sk-ant-[a-zA-Z0-9\-]{20,}"),
        re.compile(r"gsk_[a-zA-Z0-9\-_]{20,}"),
        re.compile(r"AIza[a-zA-Z0-9\-_]{35}"),
        re.compile(r'["\']([a-zA-Z0-9\-_]{32,})["\']'),
    ]

    def __init__(self, additional_patterns: list[re.Pattern[str]] | None = None) -> None:
        self.patterns = self.DEFAULT_PATTERNS.copy()
        if additional_patterns:
            self.patterns.extend(additional_patterns)

    def mask(self, text: str) -> str:
        """Mask secret-looking values inside a text blob."""
        result = text
        for pattern in self.patterns:
            result = pattern.sub(self.MASK, result)
        return result

    def mask_dict(self, data: dict, sensitive_keys: list[str] | None = None) -> dict:
        """Recursively mask sensitive values in a mapping."""
        sensitive = sensitive_keys or [
            "api_key",
            "apikey",
            "secret",
            "password",
            "token",
            "authorization",
            "bearer",
            "credential",
        ]
        result = {}
        for key, value in data.items():
            if any(s in key.lower() for s in sensitive):
                result[key] = self.MASK
            elif isinstance(value, dict):
                result[key] = self.mask_dict(value, sensitive_keys)
            elif isinstance(value, str):
                result[key] = self.mask(value)
            else:
                result[key] = value
        return result
