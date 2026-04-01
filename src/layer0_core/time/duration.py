"""Duration value object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Duration:
    """Immutable duration in seconds."""

    seconds: float

    def __post_init__(self) -> None:
        """Validate duration bounds."""
        if self.seconds < 0:
            raise ValueError(f"Duration cannot be negative: {self.seconds}")

    @property
    def milliseconds(self) -> int:
        """Return the duration in milliseconds."""
        return int(self.seconds * 1000)
