"""Extract citations from generated answers."""

from __future__ import annotations

import re

from src.layer1_contracts.schemas.answer import Citation
from src.layer1_contracts.schemas.evidence import EvidenceBundle


class CitationExtractor:
    """Extract citation references from generated text."""

    CITATION_PATTERN = re.compile(r'\[(\d+)\]')

    def extract(self, text: str, evidence_bundle: EvidenceBundle) -> list[Citation]:
        """Map cited indices back to evidence items."""
        citation_indices = sorted({int(match) for match in self.CITATION_PATTERN.findall(text)})
        citations: list[Citation] = []
        for index in citation_indices:
            if 1 <= index <= len(evidence_bundle.items):
                item = evidence_bundle.items[index - 1]
                citations.append(
                    Citation(
                        citation_key=f"[{index}]",
                        chunk_id=item.chunk_id,
                        document_id=item.document_id,
                        document_title=item.document_title,
                        page_numbers=list(item.page_numbers),
                    )
                )
        return citations
