"""Score normalization helpers."""

from __future__ import annotations


class ScoreNormalizer:
    """Normalize scores across retrieval stages."""

    @staticmethod
    def min_max_normalize(scores: list[float]) -> list[float]:
        """Normalize a score list to the 0-1 range."""
        if not scores:
            return []
        minimum = min(scores)
        maximum = max(scores)
        if maximum == minimum:
            return [0.5] * len(scores)
        return [(score - minimum) / (maximum - minimum) for score in scores]

    @staticmethod
    def z_score_normalize(scores: list[float]) -> list[float]:
        """Apply z-score normalization."""
        if not scores:
            return []
        mean = sum(scores) / len(scores)
        variance = sum((score - mean) ** 2 for score in scores) / len(scores)
        if variance == 0:
            return [0.0] * len(scores)
        std_dev = variance**0.5
        return [(score - mean) / std_dev for score in scores]
