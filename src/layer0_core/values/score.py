"""Scoring value object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Score:
    """Unbounded score with source attribution."""

    value: float
    source: str

    def normalize(self, min_val: float, max_val: float) -> "Score":
        """Normalize the score to the 0.0-1.0 range."""
        if max_val == min_val:
            normalized = 0.5
        else:
            normalized = (self.value - min_val) / (max_val - min_val)
        return Score(value=max(0.0, min(1.0, normalized)), source=f"{self.source}_normalized")
