"""Answer parsing helpers."""

from __future__ import annotations

from src.layer1_contracts.schemas.answer import Citation
from src.layer1_contracts.schemas.evidence import EvidenceBundle
from src.layer2_domain.citations.extractor import CitationExtractor
from src.layer2_domain.citations.validator import CitationValidator


class AnswerParser:
    """Parse and validate generated answers."""

    def __init__(self, extractor: CitationExtractor, validator: CitationValidator) -> None:
        self.extractor = extractor
        self.validator = validator

    def parse(self, text: str, evidence_bundle: EvidenceBundle) -> tuple[list[Citation], bool, list[str]]:
        """Extract citations and validate them against the evidence bundle."""
        citations = self.extractor.extract(text, evidence_bundle)
        is_valid, issues = self.validator.validate(text, citations, evidence_bundle)
        return citations, is_valid, issues
