"""Validate extracted citations against evidence."""

from __future__ import annotations

from src.layer1_contracts.schemas.answer import Citation
from src.layer1_contracts.schemas.evidence import EvidenceBundle


class CitationValidator:
    """Validate that cited references are grounded in the evidence bundle."""

    def validate(
        self,
        answer_text: str,
        citations: list[Citation],
        evidence_bundle: EvidenceBundle,
    ) -> tuple[bool, list[str]]:
        """Return whether the citations are valid and any issues found."""
        issues: list[str] = []
        valid_keys = {item.citation_key for item in evidence_bundle.items}
        for citation in citations:
            if citation.citation_key not in valid_keys:
                issues.append(f"Citation {citation.citation_key} not in evidence")

        for sentence in answer_text.split('.'):
            sentence = sentence.strip()
            if len(sentence) > 50 and '[' not in sentence and not self._is_boilerplate(sentence):
                issues.append(f"Potentially uncited claim: '{sentence[:50]}...'")

        return len(issues) == 0, issues

    def _is_boilerplate(self, text: str) -> bool:
        boilerplate_phrases = [
            "based on the evidence",
            "in conclusion",
            "to summarize",
            "the evidence shows",
            "according to the sources",
        ]
        lowered = text.lower()
        return any(phrase in lowered for phrase in boilerplate_phrases)
