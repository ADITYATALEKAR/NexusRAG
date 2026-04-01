"""Grounding validation helpers."""

from __future__ import annotations

from src.layer1_contracts.schemas.answer import Citation
from src.layer1_contracts.schemas.evidence import EvidenceBundle


class GroundingValidator:
    """Validate that generated answers are sufficiently grounded in evidence."""

    def validate(
        self,
        answer_text: str,
        citations: list[Citation],
        evidence_bundle: EvidenceBundle,
        threshold: float,
    ) -> tuple[bool, float, list[str]]:
        """Return whether the answer meets the grounding threshold."""
        issues: list[str] = []
        substantive_sentences = [
            sentence.strip()
            for sentence in answer_text.split('.')
            if len(sentence.strip()) > 40
        ]
        if not substantive_sentences:
            return True, 1.0, []

        cited_sentences = [sentence for sentence in substantive_sentences if '[' in sentence and ']' in sentence]
        score = len(cited_sentences) / len(substantive_sentences)
        if not citations and evidence_bundle.items:
            issues.append("Answer contains no citations")
        if score < threshold:
            issues.append(f"Grounding score {score:.2f} below threshold {threshold:.2f}")
        return score >= threshold, score, issues
