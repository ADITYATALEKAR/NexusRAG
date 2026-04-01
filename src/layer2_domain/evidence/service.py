"""Evidence assembly service."""

from __future__ import annotations

from datetime import datetime, timezone

from src.layer1_contracts.schemas.evidence import EvidenceAssemblyResult, EvidenceBundle, EvidenceConfig
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.retrieval import RetrievalCandidate
from src.layer2_domain.evidence.orderer import EvidenceOrderer, OrderingStrategy
from src.layer2_domain.evidence.selector import EvidenceSelector
from src.layer2_domain.evidence.windower import ContextWindowManager


class EvidenceService:
    """Assemble retrieval candidates into an evidence bundle."""

    def __init__(
        self,
        selector: EvidenceSelector,
        windower: ContextWindowManager,
        orderer: EvidenceOrderer,
    ) -> None:
        self.selector = selector
        self.windower = windower
        self.orderer = orderer

    async def assemble(
        self,
        candidates: list[RetrievalCandidate],
        query: Query,
        config: EvidenceConfig,
    ) -> EvidenceAssemblyResult:
        """Select, fit, and order evidence for generation."""
        start = datetime.now(timezone.utc)
        selected = self.selector.select(candidates, config)
        items_dropped = max(0, len(candidates) - len(selected))

        fitted, total_tokens = self.windower.fit_to_window(selected, config.max_total_tokens)
        items_truncated = sum(1 for item in fitted if item.was_truncated)
        ordered = fitted if config.preserve_order else self.orderer.order(fitted, OrderingStrategy.RELEVANCE)

        for index, item in enumerate(ordered):
            item.citation_key = f"[{index + 1}]"

        bundle = EvidenceBundle(
            query_id=query.id,
            items=ordered,
            total_candidates_considered=len(candidates),
            selection_strategy=config.selection_strategy.value,
            total_tokens=total_tokens,
            max_tokens_allowed=config.max_total_tokens,
            min_relevance_score=min((item.relevance_score for item in ordered), default=None),
            max_relevance_score=max((item.relevance_score for item in ordered), default=None),
            avg_relevance_score=(sum(item.relevance_score for item in ordered) / len(ordered)) if ordered else None,
        )

        elapsed_ms = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
        return EvidenceAssemblyResult(
            bundle=bundle,
            total_tokens=total_tokens,
            items_selected=len(ordered),
            items_truncated=items_truncated,
            items_dropped=items_dropped,
            assembly_time_ms=elapsed_ms,
        )
