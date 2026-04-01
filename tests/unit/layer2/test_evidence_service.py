"""Unit tests for evidence assembly."""

from __future__ import annotations

import pytest

from src.layer1_contracts.schemas.evidence import EvidenceConfig, EvidenceSelectionStrategy
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.retrieval import RetrievalCandidate, RetrievalScores, RetrievalSource
from src.layer2_domain.evidence.orderer import EvidenceOrderer
from src.layer2_domain.evidence.selector import EvidenceSelector
from src.layer2_domain.evidence.service import EvidenceService
from src.layer2_domain.evidence.windower import ContextWindowManager


def _candidate(
    chunk_id: str,
    document_id: str,
    content: str,
    score: float,
    rank: int,
) -> RetrievalCandidate:
    return RetrievalCandidate(
        chunk_id=chunk_id,
        document_id=document_id,
        content=content,
        scores=RetrievalScores(final_score=score),
        source=RetrievalSource.HYBRID,
        rank=rank,
        document_title=document_id,
        section_title="Section",
        page_numbers=[rank + 1],
    )


@pytest.mark.asyncio
async def test_evidence_service_respects_max_items_and_token_limits() -> None:
    """Evidence assembly should cap both selected items and token usage."""
    service = EvidenceService(
        selector=EvidenceSelector(),
        windower=ContextWindowManager(chars_per_token=4),
        orderer=EvidenceOrderer(),
    )
    candidates = [
        _candidate("chunk-1", "doc-1", "A" * 320, 0.95, 0),
        _candidate("chunk-2", "doc-2", "B" * 320, 0.85, 1),
        _candidate("chunk-3", "doc-3", "C" * 320, 0.75, 2),
    ]

    result = await service.assemble(
        candidates=candidates,
        query=Query(id="query-1", text="What changed?"),
        config=EvidenceConfig(max_evidence_items=2, max_total_tokens=650),
    )

    assert result.items_selected <= 2
    assert result.total_tokens <= 150
    assert len(result.bundle.items) <= 2
    assert result.bundle.items[0].citation_key == "[1]"


def test_mmr_selection_prefers_diverse_evidence() -> None:
    """MMR selection should avoid picking near-duplicate evidence when an alternative exists."""
    selector = EvidenceSelector()
    candidates = [
        _candidate("chunk-1", "doc-1", "vector retrieval dense lexical fusion reranking", 0.96, 0),
        _candidate("chunk-2", "doc-1", "vector retrieval dense lexical fusion reranking repeated", 0.92, 1),
        _candidate("chunk-3", "doc-2", "provider failover cooldown retry health checks", 0.90, 2),
    ]

    selected = selector.select(
        candidates,
        EvidenceConfig(
            max_evidence_items=2,
            max_total_tokens=800,
            min_relevance_score=0.0,
            selection_strategy=EvidenceSelectionStrategy.MMR,
        ),
    )

    assert len(selected) == 2
    assert selected[0].document_id == "doc-1"
    assert selected[1].document_id == "doc-2"
