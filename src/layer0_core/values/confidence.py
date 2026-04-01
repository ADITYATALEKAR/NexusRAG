"""Confidence value object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Confidence:
    """Confidence score bounded to the 0.0-1.0 range."""

    value: float

    def __post_init__(self) -> None:
        """Validate score bounds."""
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got: {self.value}")

    @classmethod
    def low(cls) -> "Confidence":
        """Return a low confidence score."""
        return cls(0.2)

    @classmethod
    def medium(cls) -> "Confidence":
        """Return a medium confidence score."""
        return cls(0.5)

    @classmethod
    def high(cls) -> "Confidence":
        """Return a high confidence score."""
        return cls(0.85)

    def is_above(self, threshold: float) -> bool:
        """Return whether the score meets the threshold."""
        return self.value >= threshold
