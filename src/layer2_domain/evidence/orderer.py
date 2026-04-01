"""Evidence ordering strategies."""

from __future__ import annotations

from enum import Enum

from src.layer1_contracts.schemas.evidence import EvidenceItem


class OrderingStrategy(str, Enum):
    """Supported evidence ordering strategies."""

    RELEVANCE = "relevance"
    CHRONOLOGICAL = "chronological"
    DOCUMENT_ORDER = "document_order"
    REVERSE_RELEVANCE = "reverse_relevance"


class EvidenceOrderer:
    """Reorder evidence items for prompt construction."""

    def order(
        self,
        items: list[EvidenceItem],
        strategy: OrderingStrategy = OrderingStrategy.RELEVANCE,
    ) -> list[EvidenceItem]:
        """Return items ordered according to the selected strategy."""
        if strategy == OrderingStrategy.RELEVANCE:
            return sorted(items, key=lambda item: item.relevance_score, reverse=True)
        if strategy == OrderingStrategy.REVERSE_RELEVANCE:
            return sorted(items, key=lambda item: item.relevance_score)
        if strategy == OrderingStrategy.DOCUMENT_ORDER:
            return sorted(
                items,
                key=lambda item: (item.document_id, item.page_numbers[0] if item.page_numbers else 0),
            )
        return list(items)
