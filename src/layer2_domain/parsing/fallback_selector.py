"""Fallback parser selection."""

from __future__ import annotations

from src.layer1_contracts.schemas.parsing import ParseResult


class FallbackSelector:
    """Choose whether a fallback parser should replace the primary result."""

    def __init__(self, min_confidence: float = 0.3) -> None:
        self.min_confidence = min_confidence

    def should_use_fallback(self, result: ParseResult) -> bool:
        """Return whether the primary parse result is too weak to trust."""
        return result.confidence < self.min_confidence

    def select(self, primary: ParseResult, fallback: ParseResult) -> ParseResult:
        """Choose the better parse result."""
        return fallback if fallback.confidence > primary.confidence else primary
