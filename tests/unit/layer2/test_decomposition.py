"""Unit tests for bounded decomposition."""

from __future__ import annotations

from typing import cast

from src.layer1_contracts.schemas.decomposition import SubQueryResult
from src.layer1_contracts.schemas.query import Query, QueryType
from src.layer1_contracts.schemas.query_understanding import QueryAnalysis, QueryComplexity, QueryIntent
from src.layer2_domain.decomposition.aggregator import SubAnswerAggregator
from src.layer2_domain.decomposition.comparative import ComparativeDecomposer
from src.layer2_domain.decomposition.two_hop import TwoHopDecomposer
from src.layer2_domain.generation.service import GenerationService


def test_comparative_decomposer_uses_analysis_sub_queries() -> None:
    """Comparative decomposition should preserve classifier-generated sub-queries."""
    decomposer = ComparativeDecomposer()
    analysis = QueryAnalysis(
        query_id="query-1",
        original_text="Compare Python vs Go",
        cleaned_text="Compare Python vs Go",
        query_type=QueryType.COMPARATIVE,
        intent=QueryIntent.COMPARATIVE,
        complexity=QueryComplexity.COMPLEX,
        sub_queries=["What is Python?", "What is Go?", "Key differences between Python and Go"],
        confidence=0.9,
        analysis_time_ms=1,
    )

    plan = decomposer.decompose(Query(id="query-1", text="Compare Python vs Go"), analysis)

    assert plan.strategy == "comparative"
    assert len(plan.sub_queries) == 3
    assert plan.sub_queries[0].depends_on == []


def test_two_hop_decomposer_builds_ordered_plan() -> None:
    """Two-hop decomposition should create a dependency from hop 2 to hop 1."""
    decomposer = TwoHopDecomposer()
    analysis = QueryAnalysis(
        query_id="query-2",
        original_text="Who is the CEO of the company that made Pixel?",
        cleaned_text="Who is the CEO of the company that made Pixel?",
        query_type=QueryType.MULTI_HOP,
        intent=QueryIntent.FACTUAL,
        complexity=QueryComplexity.COMPLEX,
        confidence=0.8,
        analysis_time_ms=1,
    )

    plan = decomposer.decompose(
        Query(id="query-2", text="Who is the CEO of the company that made Pixel?"),
        analysis,
    )

    assert plan.strategy == "two_hop"
    assert len(plan.sub_queries) == 2
    assert plan.sub_queries[1].depends_on == ["query-2-hop1"]


async def test_sub_answer_aggregator_returns_last_two_hop_result() -> None:
    """Sequential aggregation should surface the last bounded hop answer."""
    aggregator = SubAnswerAggregator(cast(GenerationService, object()))
    sub_results = [
        SubQueryResult(sub_query_id="hop1", answer="Google", evidence_used=["chunk-1"], confidence=0.8),
        SubQueryResult(sub_query_id="hop2", answer="Sundar Pichai", evidence_used=["chunk-2"], confidence=0.9),
    ]

    aggregated = await aggregator.aggregate(
        Query(id="query-3", text="Who is the CEO of the company that made Pixel?"),
        sub_results,
        "two_hop",
    )

    assert aggregated.final_answer == "Sundar Pichai"
    assert aggregated.total_evidence == ["chunk-1", "chunk-2"]
