"""Parse quality assessment."""

from __future__ import annotations

from src.layer1_contracts.schemas.parsing import ParseResult


class ParseQualityChecker:
    """Assess parse quality and normalize confidence scores."""

    def assess(self, result: ParseResult) -> float:
        """Return an adjusted parse confidence score."""
        if not result.pages:
            return min(result.confidence, 0.2)

        total_chars = len(result.raw_text.strip())
        avg_chars_per_page = total_chars / max(1, len(result.pages))
        if avg_chars_per_page <= 25:
            return min(result.confidence, 0.2)
        if avg_chars_per_page <= 100:
            return min(result.confidence, 0.4)
        if avg_chars_per_page <= 250:
            return max(result.confidence, 0.6)
        return max(result.confidence, 0.8)
