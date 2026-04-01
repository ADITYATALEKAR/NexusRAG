"""Main Phase 5 routed query flow."""

from __future__ import annotations

from src.layer1_contracts.schemas.answer import Answer, AnswerMetadata, AnswerStatus
from src.layer1_contracts.schemas.decomposition import SubQueryResult
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.retrieval_config import RetrievalConfig, RetrievalMode
from src.layer1_contracts.schemas.routing import Route, RouteType, RoutingDecision, RoutingDiagnostics
from src.layer1_contracts.schemas.security import SecurityDecisionType
from src.layer1_contracts.schemas.structured import StructuredQuery, StructuredQueryType
from src.layer2_domain.decomposition.aggregator import SubAnswerAggregator
from src.layer2_domain.decomposition.comparative import ComparativeDecomposer
from src.layer2_domain.decomposition.two_hop import TwoHopDecomposer
from src.layer2_domain.routing.fallback_handler import FallbackHandler
from src.layer2_domain.routing.router import QueryRouter
from src.layer2_domain.structured_retrieval.service import StructuredRetrievalService
from src.layer3_flows.answer_flow.flow import AnswerFlow
from src.layer3_flows.multi_hop_flow.flow import MultiHopFlow
from src.layer3_flows.routed_query_flow.states import RoutedQueryContext, RoutedQueryState
from src.layer3_flows.routed_query_flow.steps import RouteDecisionStep, RouteExecutionStep, SecurityCheckStep
from src.layer3_flows.structured_query_flow.flow import StructuredQueryFlow
from src.layer6_security.query_safety.injection_guard import QueryInjectionGuard
from src.layer6_security.query_safety.output_guard import AnswerOutputGuard
from src.layer6_security.query_safety.scope_validator import QueryScopeValidator


class RoutedQueryFlow:
    """Route queries to bounded handlers with security and fallback rails."""

    def __init__(
        self,
        router: QueryRouter,
        injection_guard: QueryInjectionGuard,
        scope_validator: QueryScopeValidator,
        fallback_handler: FallbackHandler,
        standard_flow: AnswerFlow,
        structured_service: StructuredRetrievalService,
        comparative_decomposer: ComparativeDecomposer,
        two_hop_decomposer: TwoHopDecomposer,
        aggregator: SubAnswerAggregator,
        output_guard: AnswerOutputGuard | None = None,
    ) -> None:
        self.router = router
        self.injection_guard = injection_guard
        self.scope_validator = scope_validator
        self.fallback_handler = fallback_handler
        self.standard_flow = standard_flow
        self.structured_service = structured_service
        self.comparative_decomposer = comparative_decomposer
        self.two_hop_decomposer = two_hop_decomposer
        self.aggregator = aggregator
        self.output_guard = output_guard or AnswerOutputGuard()
        self.security_step = SecurityCheckStep()
        self.route_step = RouteDecisionStep()
        self.execution_step = RouteExecutionStep()

    async def execute(
        self,
        query: Query,
        forced_route: RouteType | None = None,
    ) -> tuple[Answer, RoutingDiagnostics | None]:
        """Execute the routed query flow end to end."""
        context = RoutedQueryContext(query=query, forced_route=forced_route)
        if not await self.security_step.execute(self, context):
            return context.answer or self._blocked_answer(query, "Security policy rejected the query"), None

        await self.route_step.execute(self, context)
        try:
            await self.execution_step.execute(self, context)
        except Exception as error:  # noqa: BLE001
            context.state = RoutedQueryState.FAILED
            context.error = str(error)
            if not self.fallback_handler.trigger_on_error:
                raise
            original_route = (
                context.routing_decision.selected_route
                if context.routing_decision is not None
                else self._standard_route()
            )
            fallback_answer, final_route = await self.fallback_handler.execute_fallback(
                original_route=original_route,
                query=query,
                standard_executor=self.standard_flow,
            )
            context.answer = self.output_guard.guard(fallback_answer)
            context.diagnostics = RoutingDiagnostics(
                query_id=query.id,
                selected_route=original_route.route_type,
                route_confidence=original_route.confidence,
                classifier_scores=self.router.get_scores(query.id),
                fallback_triggered=True,
                fallback_reason=str(error),
                final_route_used=final_route,
            )
            return context.answer, context.diagnostics

        if context.answer is None:
            raise ValueError("Routed query flow completed without an answer")
        context.answer = self.output_guard.guard(context.answer)
        return context.answer, context.diagnostics

    def _run_security_checks(self, query: Query) -> Answer | None:
        injection_check = self.injection_guard.check(query.text)
        if injection_check.decision == SecurityDecisionType.DENY:
            return self._blocked_answer(query, injection_check.reason or "Potential prompt injection detected")

        scope_check = self.scope_validator.validate(query.text)
        if scope_check.decision == SecurityDecisionType.DENY:
            return self._blocked_answer(query, scope_check.reason or "Query blocked by scope policy")
        return None

    def _build_routing_decision(
        self,
        query: Query,
        forced_route: RouteType | None,
    ) -> RoutingDecision:
        decision = self.router.route(query)
        if forced_route is None:
            return decision
        forced_selected = decision.selected_route.model_copy(
            update={
                "route_type": forced_route,
                "confidence": 1.0,
                "reasoning": f"{decision.selected_route.reasoning}; force_route={forced_route.value}",
            }
        )
        return decision.model_copy(update={"selected_route": forced_selected})

    async def _execute_routed(
        self,
        query: Query,
        routing_decision: RoutingDecision,
    ) -> tuple[Answer, RoutingDiagnostics]:
        route = routing_decision.selected_route
        should_fallback, fallback_reason = self.fallback_handler.should_fallback(route)
        if should_fallback and route.route_type != RouteType.STANDARD:
            fallback_answer, final_route = await self.fallback_handler.execute_fallback(
                original_route=route,
                query=query,
                standard_executor=self.standard_flow,
            )
            return fallback_answer, self._build_diagnostics(
                query_id=query.id,
                route_type=route.route_type,
                route_confidence=route.confidence,
                fallback_triggered=True,
                fallback_reason=fallback_reason,
                final_route=final_route,
            )

        answer = await self._handle_route(query, routing_decision)
        return answer, self._build_diagnostics(
            query_id=query.id,
            route_type=route.route_type,
            route_confidence=route.confidence,
            fallback_triggered=False,
            fallback_reason=None,
            final_route=route.route_type,
        )

    async def _handle_route(self, query: Query, routing_decision: RoutingDecision) -> Answer:
        route = routing_decision.selected_route
        analysis = routing_decision.query_analysis
        if route.route_type == RouteType.STANDARD:
            answer, _ = await self.standard_flow.execute(query)
            return answer
        if route.route_type == RouteType.KEYWORD_HEAVY:
            config = self._build_weighted_config(
                lexical_weight=float(route.parameters.get("lexical_weight", 0.7)),
                dense_weight=float(route.parameters.get("dense_weight", 0.3)),
            )
            answer, _ = await self.standard_flow.execute(query, retrieval_config=config)
            return answer
        if route.route_type == RouteType.SEMANTIC_HEAVY:
            config = self._build_weighted_config(
                lexical_weight=float(route.parameters.get("lexical_weight", 0.3)),
                dense_weight=float(route.parameters.get("dense_weight", 0.7)),
            )
            answer, _ = await self.standard_flow.execute(query, retrieval_config=config)
            return answer
        if route.route_type == RouteType.STRUCTURED:
            return await self._handle_structured(query, analysis, route.parameters)
        if route.route_type == RouteType.COMPARATIVE:
            return await self._handle_comparative(query, analysis, route.parameters)
        if route.route_type == RouteType.TWO_HOP:
            return await self._handle_two_hop(query, analysis, route.parameters)
        answer, _ = await self.standard_flow.execute(query)
        return answer

    def _build_weighted_config(self, lexical_weight: float, dense_weight: float) -> RetrievalConfig:
        base_config = self.standard_flow.retrieval_service.default_config.model_copy(deep=True)
        return base_config.model_copy(
            update={
                "mode": RetrievalMode.HYBRID,
                "lexical_weight": lexical_weight,
                "dense_weight": dense_weight,
            }
        )

    async def _handle_structured(self, query: Query, analysis, route_parameters: dict[str, object]) -> Answer:
        del analysis
        structured_flow = StructuredQueryFlow(self.structured_service)
        default_table = str(route_parameters.get("default_table", "documents"))
        try:
            result = await structured_flow.execute(query)
        except Exception:  # noqa: BLE001
            result = await structured_flow.execute(
                query,
                structured_query=StructuredQuery(
                    id=query.id,
                    natural_query=query.text,
                    query_type=StructuredQueryType.LOOKUP,
                    target_table=default_table,
                    columns=["*"],
                ),
            )
        return Answer(
            id=f"ans-{query.id}",
            query_id=query.id,
            text=result.formatted_answer or "No results found",
            status=AnswerStatus.SUCCESS if result.rows else AnswerStatus.ABSTAINED,
            citations=[],
            metadata=AnswerMetadata(
                model_used="structured_sql",
                provider_used="internal",
                fallback_occurred=False,
                fallback_chain=[],
            ),
        )

    async def _handle_comparative(self, query: Query, analysis, route_parameters: dict[str, object]) -> Answer:
        plan = self.comparative_decomposer.decompose(query, analysis)
        max_sub_queries = int(route_parameters.get("max_sub_queries", len(plan.sub_queries) or 3))
        sub_results: list[SubQueryResult] = []
        for sub_query in plan.sub_queries[:max_sub_queries]:
            sub_answer, _ = await self.standard_flow.execute(Query(id=sub_query.id, text=sub_query.text))
            sub_results.append(
                SubQueryResult(
                    sub_query_id=sub_query.id,
                    answer=sub_answer.text,
                    evidence_used=[citation.chunk_id for citation in sub_answer.citations],
                    confidence=0.8,
                )
            )
        aggregated = await self.aggregator.aggregate(query, sub_results, "comparative")
        return Answer(
            id=f"ans-{query.id}",
            query_id=query.id,
            text=aggregated.final_answer,
            status=AnswerStatus.SUCCESS,
            citations=[],
            metadata=AnswerMetadata(
                model_used="comparative_synthesis",
                provider_used="internal",
                fallback_occurred=False,
                fallback_chain=[],
            ),
        )

    async def _handle_two_hop(self, query: Query, analysis, route_parameters: dict[str, object]) -> Answer:
        max_hops = int(route_parameters.get("max_hops", 2))
        if max_hops < 2:
            fallback_answer, _ = await self.standard_flow.execute(query)
            return fallback_answer
        multi_hop_flow = MultiHopFlow(self.standard_flow, self.two_hop_decomposer, self.aggregator)
        aggregated = await multi_hop_flow.execute(query, analysis)
        return Answer(
            id=f"ans-{query.id}",
            query_id=query.id,
            text=aggregated.final_answer,
            status=AnswerStatus.SUCCESS,
            citations=[],
            metadata=AnswerMetadata(
                model_used="two_hop",
                provider_used="internal",
                fallback_occurred=False,
                fallback_chain=[],
            ),
        )

    def _standard_route(self) -> Route:
        """Return a synthetic standard route for fallback diagnostics."""
        return Route(
            route_type=RouteType.STANDARD,
            confidence=0.0,
            reasoning="Fallback after route execution failure",
            fallback_route=RouteType.STANDARD,
            parameters={},
        )

    def _build_diagnostics(
        self,
        query_id: str,
        route_type: RouteType,
        route_confidence: float,
        fallback_triggered: bool,
        fallback_reason: str | None,
        final_route: RouteType,
    ) -> RoutingDiagnostics:
        return RoutingDiagnostics(
            query_id=query_id,
            selected_route=route_type,
            route_confidence=route_confidence,
            classifier_scores=self.router.get_scores(query_id),
            fallback_triggered=fallback_triggered,
            fallback_reason=fallback_reason,
            final_route_used=final_route,
        )

    def _blocked_answer(self, query: Query, reason: str) -> Answer:
        return Answer(
            id=f"ans-{query.id}",
            query_id=query.id,
            text=f"I cannot process this query: {reason}",
            status=AnswerStatus.FILTERED,
            citations=[],
            safety_filtered=True,
            safety_filter_reason=reason,
            metadata=AnswerMetadata(
                model_used="none",
                provider_used="security",
                fallback_occurred=False,
                fallback_chain=[],
            ),
        )
