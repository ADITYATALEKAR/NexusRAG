"""Abstention checks for answer generation."""

from __future__ import annotations

from src.layer1_contracts.schemas.evidence import EvidenceBundle
from src.layer1_contracts.schemas.generation import AbstentionReason


class AbstentionChecker:
    """Determine if the system should abstain from answering."""

    ABSTENTION_PHRASES = [
        "cannot answer",
        "insufficient evidence",
        "not enough information",
        "unable to determine",
        "no relevant information",
        "cannot be determined from",
        "evidence does not",
        "i don't have enough",
    ]

    def __init__(
        self,
        min_evidence_items: int = 1,
        min_relevance_score: float = 0.3,
        min_avg_relevance: float = 0.4,
    ) -> None:
        self.min_evidence_items = min_evidence_items
        self.min_relevance_score = min_relevance_score
        self.min_avg_relevance = min_avg_relevance

    def should_abstain_before_generation(
        self,
        evidence_bundle: EvidenceBundle,
    ) -> tuple[bool, AbstentionReason | None]:
        """Check if the system should abstain before calling an LLM."""
        if len(evidence_bundle.items) < self.min_evidence_items:
            return True, AbstentionReason.INSUFFICIENT_EVIDENCE
        if (
            evidence_bundle.max_relevance_score is not None
            and evidence_bundle.max_relevance_score < self.min_relevance_score
        ):
            return True, AbstentionReason.LOW_CONFIDENCE
        if (
            evidence_bundle.avg_relevance_score is not None
            and evidence_bundle.avg_relevance_score < self.min_avg_relevance
        ):
            return True, AbstentionReason.LOW_CONFIDENCE
        return False, None

    def detect_abstention_in_response(
        self,
        response_text: str,
    ) -> tuple[bool, AbstentionReason | None]:
        """Detect abstention language in an LLM response."""
        lowered = response_text.lower()
        for phrase in self.ABSTENTION_PHRASES:
            if phrase in lowered:
                return True, AbstentionReason.INSUFFICIENT_EVIDENCE
        return False, None
