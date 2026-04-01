"""Unit tests for the Phase 5 query router."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.layer1_contracts.schemas.answer import Answer, AnswerMetadata, AnswerStatus
from src.layer1_contracts.schemas.generation import GenerationTrace
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.retrieval_config import RetrievalConfig
from src.layer1_contracts.schemas.routing import Route, RouteType
from src.layer2_domain.query_understanding.classifier import QueryClassifier
from src.layer2_domain.routing.confidence_scorer import RoutingConfidenceScorer
from src.layer2_domain.routing.fallback_handler import FallbackHandler
from src.layer2_domain.routing.route_selector import RouteSelector
from src.layer2_domain.routing.router import QueryRouter


def _build_router() -> QueryRouter:
    return QueryRouter(
        classifier=QueryClassifier(),
        confidence_scorer=RoutingConfidenceScorer(),
        route_selector=RouteSelector(),
    )


def test_router_selects_keyword_heavy_route() -> None:
    """Keyword-heavy queries should bias lexical retrieval."""
    router = _build_router()

    decision = router.route(Query(id="query-1", text='"RFC 9110"'))

    assert decision.selected_route.route_type == RouteType.KEYWORD_HEAVY
    assert float(decision.selected_route.parameters["lexical_weight"]) > float(
        decision.selected_route.parameters["dense_weight"]
    )


def test_router_selects_semantic_heavy_route() -> None:
    """Semantic queries should bias dense retrieval."""
    router = _build_router()

    decision = router.route(Query(id="query-2", text="Explain vector embeddings in semantic search"))

    assert decision.selected_route.route_type == RouteType.SEMANTIC_HEAVY
    assert float(decision.selected_route.parameters["dense_weight"]) > float(
        decision.selected_route.parameters["lexical_weight"]
    )


def test_router_selects_structured_route() -> None:
    """Aggregation-style queries should route to structured retrieval."""
    router = _build_router()

    decision = router.route(Query(id="query-3", text="How many documents are indexed?"))

    assert decision.selected_route.route_type == RouteType.STRUCTURED
    assert decision.query_analysis.requires_structured is True


def test_fallback_handler_triggers_on_low_confidence() -> None:
    """Low-confidence routes should fall back to safer paths."""
    handler = FallbackHandler(confidence_threshold=0.9)
    route = Route(
        route_type=RouteType.SEMANTIC_HEAVY,
        confidence=0.7,
        reasoning="semantic route",
        fallback_route=RouteType.STANDARD,
    )

    should_fallback, reason = handler.should_fallback(route)

    assert should_fallback is True
    assert "below threshold" in reason


def test_router_uses_configured_route_weights() -> None:
    """Route-specific config should override the built-in lexical/dense defaults."""
    router = QueryRouter(
        classifier=QueryClassifier(),
        confidence_scorer=RoutingConfidenceScorer(),
        route_selector=RouteSelector(),
        route_configs={
            "keyword_heavy": {
                "lexical_weight": 0.9,
                "dense_weight": 0.1,
            }
        },
    )

    decision = router.route(Query(id="query-config-1", text='"RFC 9110"'))

    assert decision.selected_route.route_type == RouteType.KEYWORD_HEAVY
    assert decision.selected_route.parameters["lexical_weight"] == 0.9
    assert decision.selected_route.parameters["dense_weight"] == 0.1


def test_router_disables_two_hop_when_max_hops_is_one() -> None:
    """Two-hop routing should be disabled when the configured hop ceiling is lower."""
    router = QueryRouter(
        classifier=QueryClassifier(),
        confidence_scorer=RoutingConfidenceScorer(),
        route_selector=RouteSelector(),
        max_decomposition_hops=1,
    )

    decision = router.route(Query(id="query-config-2", text="Who is the CEO of the company that made Pixel?"))

    assert decision.selected_route.route_type == RouteType.STANDARD


class StubStandardExecutor:
    """Minimal standard-path stub for fallback handler unit tests."""

    def __init__(self) -> None:
        self.calls: list[RetrievalConfig | None] = []

    async def execute(
        self,
        query: Query,
        retrieval_config: RetrievalConfig | None = None,
        evidence_config=None,
        generation_config=None,
    ) -> tuple[Answer, GenerationTrace]:
        del evidence_config, generation_config
        self.calls.append(retrieval_config)
        answer = Answer(
            id=f"ans-{query.id}",
            query_id=query.id,
            text="fallback answer",
            status=AnswerStatus.SUCCESS,
            citations=[],
            metadata=AnswerMetadata(model_used="stub", provider_used="stub"),
        )
        trace = GenerationTrace(
            request_id=query.id,
            query_text=query.text,
            evidence_items=[],
            prompt_tokens=0,
            completion_tokens=0,
            provider_used="stub",
            model_used="stub",
            fallback_occurred=False,
            fallback_chain=[],
            latency_ms=1,
            created_at=datetime.now(timezone.utc),
        )
        return answer, trace


@pytest.mark.asyncio
async def test_fallback_handler_executes_standard_fallback() -> None:
    """Fallback execution should route through the standard hybrid path."""
    handler = FallbackHandler()
    executor = StubStandardExecutor()
    route = Route(
        route_type=RouteType.COMPARATIVE,
        confidence=0.2,
        reasoning="comparative route",
        fallback_route=RouteType.STANDARD,
    )

    answer, final_route = await handler.execute_fallback(
        original_route=route,
        query=Query(id="query-fallback-exec", text="Compare A vs B"),
        standard_executor=executor,
    )

    assert answer.text == "fallback answer"
    assert final_route == RouteType.STANDARD
    assert executor.calls[0] is not None
    assert executor.calls[0].mode.value == "hybrid"
