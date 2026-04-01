"""Context window management for evidence bundles."""

from __future__ import annotations

from src.layer1_contracts.schemas.evidence import EvidenceItem
from src.layer2_domain.evidence.truncator import EvidenceTruncator


class ContextWindowManager:
    """Manage evidence within context window limits."""

    def __init__(self, tokenizer_model: str = "cl100k_base", chars_per_token: int = 4) -> None:
        self.tokenizer_model = tokenizer_model
        self.chars_per_token = chars_per_token
        self.truncator = EvidenceTruncator(chars_per_token=chars_per_token)

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count using a lightweight char heuristic."""
        return max(1, len(text) // self.chars_per_token)

    def fit_to_window(
        self,
        evidence_items: list[EvidenceItem],
        max_tokens: int,
        reserve_tokens: int = 500,
    ) -> tuple[list[EvidenceItem], int]:
        """Fit evidence items within the available token budget."""
        available_tokens = max(0, max_tokens - reserve_tokens)
        fitted: list[EvidenceItem] = []
        total_tokens = 0

        for item in evidence_items:
            item_tokens = self.estimate_tokens(item.content)
            if total_tokens + item_tokens <= available_tokens:
                copy = item.model_copy(deep=True)
                copy.token_count = item_tokens
                fitted.append(copy)
                total_tokens += item_tokens
                continue

            remaining_tokens = available_tokens - total_tokens
            if remaining_tokens > 100:
                fitted.append(self.truncator.truncate(item, remaining_tokens))
                total_tokens += remaining_tokens
            break

        return fitted, total_tokens
