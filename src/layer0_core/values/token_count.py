"""Token count value object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TokenCount:
    """Token count with model attribution."""

    count: int
    model: str

    def __post_init__(self) -> None:
        """Validate the token count."""
        if self.count < 0:
            raise ValueError(f"Token count cannot be negative: {self.count}")

    def fits_context(self, context_window: int, reserved: int = 0) -> bool:
        """Return whether the token count fits inside a model context window."""
        return self.count <= (context_window - reserved)
