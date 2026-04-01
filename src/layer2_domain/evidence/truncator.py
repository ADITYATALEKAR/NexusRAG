"""Evidence truncation helpers."""

from __future__ import annotations

from src.layer1_contracts.schemas.evidence import EvidenceItem


class EvidenceTruncator:
    """Truncate evidence items to fit token budgets."""

    def __init__(self, chars_per_token: int = 4) -> None:
        self.chars_per_token = chars_per_token

    def truncate(self, item: EvidenceItem, max_tokens: int) -> EvidenceItem:
        """Return a truncated copy of an evidence item bounded by tokens."""
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

        max_chars = max_tokens * self.chars_per_token
        content = item.content
        if len(content) <= max_chars:
            copy = item.model_copy(deep=True)
            copy.token_count = max_tokens
            return copy

        truncated = content[:max_chars]
        last_period = truncated.rfind('. ')
        if last_period > max_chars * 0.7:
            truncated = truncated[: last_period + 1]
        copy = item.model_copy(deep=True)
        copy.content = truncated.rstrip() + "..."
        copy.was_truncated = True
        copy.token_count = max_tokens
        return copy
