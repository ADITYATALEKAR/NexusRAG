"""Output safety guard for routed answers."""

from __future__ import annotations

import re

from src.layer1_contracts.schemas.answer import Answer, AnswerStatus
from src.layer6_security.secrets.masking import SecretMasker


class AnswerOutputGuard:
    """Prevent obviously unsafe routed answers from leaving the system."""

    UNSAFE_OUTPUT_PATTERNS = [
        r"system\s*prompt",
        r"</?(system|assistant|user)>",
        r"ignore previous instructions",
        r"\[INST\]|\[/INST\]",
    ]

    def __init__(self, secret_masker: SecretMasker | None = None) -> None:
        self.secret_masker = secret_masker or SecretMasker()

    def guard(self, answer: Answer) -> Answer:
        """Return a guarded answer, filtering or masking when necessary."""
        if answer.status == AnswerStatus.FILTERED and answer.safety_filtered:
            return answer

        masked_text = self.secret_masker.mask(answer.text)
        if masked_text != answer.text:
            answer = answer.model_copy(
                update={
                    "text": masked_text,
                    "safety_filtered": True,
                    "safety_filter_reason": "Secrets masked in output",
                }
            )

        for pattern in self.UNSAFE_OUTPUT_PATTERNS:
            if re.search(pattern, answer.text, re.IGNORECASE):
                return answer.model_copy(
                    update={
                        "text": "I cannot return this answer because output safety checks failed.",
                        "status": AnswerStatus.FILTERED,
                        "citations": [],
                        "safety_filtered": True,
                        "safety_filter_reason": "Unsafe output detected",
                    }
                )
        return answer
