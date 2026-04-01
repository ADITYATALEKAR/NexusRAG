"""Citation formatting helpers."""

from __future__ import annotations

from src.layer1_contracts.schemas.answer import Citation


class CitationFormatter:
    """Format citations for presentation or debugging."""

    def format(self, citations: list[Citation]) -> list[str]:
        """Return human-readable citation strings."""
        formatted: list[str] = []
        for citation in citations:
            title = citation.document_title or citation.document_id
            pages = f" p.{','.join(map(str, citation.page_numbers))}" if citation.page_numbers else ""
            formatted.append(f"{citation.citation_key} {title}{pages}")
        return formatted
