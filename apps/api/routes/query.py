"""Phase 5 query routing endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field

from apps.api.routes.answer import _get_or_build_answer_runtime
from apps.api.runtime_services import build_runtime_stores
from apps.api.runtime_storage import load_storage_runtime
from src.layer0_core.ids.base import QueryId
from src.layer1_contracts.schemas.answer import Answer
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.query_understanding import QueryAnalysis
from src.layer1_contracts.schemas.routing import RouteType, RoutingDiagnostics
from src.layer2_domain.decomposition.aggregator import SubAnswerAggregator
from src.layer2_domain.decomposition.comparative import ComparativeDecomposer
from src.layer2_domain.decomposition.two_hop import TwoHopDecomposer
from src.layer2_domain.query_understanding.classifier import QueryClassifier
from src.layer2_domain.routing.confidence_scorer import RoutingConfidenceScorer
from src.layer2_domain.routing.fallback_handler import FallbackHandler
from src.layer2_domain.routing.route_selector import RouteSelector
from src.layer2_domain.routing.router import QueryRouter
from src.layer2_domain.structured_retrieval.result_formatter import StructuredResultFormatter
from src.layer2_domain.structured_retrieval.service import StructuredRetrievalService
from src.layer2_domain.structured_retrieval.sql_generator import SafeSQLGenerator
from src.layer2_domain.structured_retrieval.template_engine import QueryTemplateEngine
from src.layer3_flows.routed_query_flow.flow import RoutedQueryFlow
from src.layer6_security.query_safety.injection_guard import QueryInjectionGuard
from src.layer6_security.query_safety.output_guard import AnswerOutputGuard
from src.layer6_security.query_safety.scope_validator import QueryScopeValidator
from src.layer8_runtime.config.loader import ConfigLoader

router = APIRouter()


class QueryRequest(BaseModel):
    """API request body for routed query execution."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(..., min_length=1)
    include_routing_diagnostics: bool = False
    force_route: RouteType | None = None


class QueryResponse(BaseModel):
    """API response body for Phase 5 routed queries."""

    model_config = ConfigDict(extra="forbid")

    answer: Answer
    routing: RoutingDiagnostics | None = None


@dataclass
class QueryRuntime:
    """Cached runtime for the Phase 5 query endpoints."""

    flow: RoutedQueryFlow
    classifier: QueryClassifier
    output_guard: AnswerOutputGuard


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(payload: QueryRequest, request: Request) -> QueryResponse:
    """Execute a routed query through the bounded Phase 5 planner."""
    runtime = await _get_or_build_query_runtime(request)
    query = Query(
        id=QueryId.generate().value,
        text=payload.query,
        request_id=getattr(request.state, "request_id", None),
    )
    answer, diagnostics = await runtime.flow.execute(query, forced_route=payload.force_route)
    return QueryResponse(
        answer=answer,
        routing=diagnostics if payload.include_routing_diagnostics else None,
    )


@router.post("/analyze", response_model=QueryAnalysis)
async def analyze_query(query: str, request: Request) -> QueryAnalysis:
    """Analyze a query without executing it."""
    classifier = _get_or_build_query_classifier(request)
    analysis = classifier.classify(query)
    return analysis.model_copy(update={"query_id": QueryId.generate().value})


@router.get("/routes", response_model=list[str])
async def list_routes() -> list[str]:
    """List the available route types."""
    return [route_type.value for route_type in RouteType]


async def _get_or_build_query_runtime(request: Request) -> QueryRuntime:
    """Return the cached Phase 5 query runtime or build it lazily."""
    runtime = getattr(request.app.state, "query_runtime", None)
    if runtime is not None:
        return runtime

    if hasattr(request.app.state, "routed_query_flow") and hasattr(request.app.state, "query_classifier"):
        runtime = QueryRuntime(
            flow=request.app.state.routed_query_flow,
            classifier=request.app.state.query_classifier,
            output_guard=getattr(request.app.state, "query_output_guard", AnswerOutputGuard()),
        )
        request.app.state.query_runtime = runtime
        return runtime

    runtime = await _build_query_runtime(request)
    request.app.state.query_runtime = runtime
    request.app.state.routed_query_flow = runtime.flow
    request.app.state.query_classifier = runtime.classifier
    request.app.state.query_output_guard = runtime.output_guard
    return runtime


async def _build_query_runtime(request: Request) -> QueryRuntime:
    """Build the Phase 5 routed query runtime from configs and shared services."""
    answer_runtime = await _get_or_build_answer_runtime(request)
    config_dir = Path(__file__).resolve().parents[3] / "configs"
    loader = ConfigLoader(config_dir=config_dir)
    routing_raw = loader.load_yaml("routing/routing.yaml").get("routing", {})
    route_raw = loader.load_yaml("routing/routes.yaml").get("routes", {})
    fallback_raw = loader.load_yaml("routing/fallback.yaml").get("fallback", {})
    structured_raw = loader.load_yaml("structured/templates.yaml").get("structured", {})
    safety_raw = loader.load_yaml("safety/query-safety.yaml").get("query_safety", {})
    routing_fallback_raw = routing_raw.get("fallback", {}) if isinstance(routing_raw.get("fallback"), dict) else {}
    fallback_route = _parse_route_type(
        routing_fallback_raw.get("fallback_route", fallback_raw.get("fallback_route", RouteType.STANDARD.value))
    )

    classifier = _get_or_build_query_classifier(request)
    router_service = QueryRouter(
        classifier=classifier,
        confidence_scorer=RoutingConfidenceScorer(),
        route_selector=RouteSelector(),
        confidence_threshold=float(routing_raw.get("confidence_threshold", 0.6)),
        enable_structured=bool(routing_raw.get("enable_structured", True)),
        enable_decomposition=bool(routing_raw.get("enable_decomposition", True)),
        max_decomposition_hops=int(routing_raw.get("max_decomposition_hops", 2)),
        route_configs={
            str(route_name): route_config
            for route_name, route_config in route_raw.items()
            if isinstance(route_config, dict)
        },
        default_fallback_route=fallback_route,
    )
    injection_guard = QueryInjectionGuard()
    scope_validator = QueryScopeValidator(
        blocked_topics=[str(topic) for topic in safety_raw.get("blocked_topics", [])],
        max_query_length=int(safety_raw.get("max_query_length", 10000)),
    )
    output_guard = AnswerOutputGuard()
    fallback_handler = FallbackHandler(
        confidence_threshold=float(fallback_raw.get("confidence_threshold", 0.55)),
        low_quality_threshold=float(fallback_raw.get("low_result_quality_threshold", 0.3)),
        fallback_route=fallback_route,
        trigger_on_low_confidence=bool(routing_fallback_raw.get("trigger_on_low_confidence", True)),
        trigger_on_error=bool(routing_fallback_raw.get("trigger_on_error", True)),
    )

    storage = load_storage_runtime(project_root=config_dir.parent)
    stores = build_runtime_stores(storage, embed_dimensions=384)
    sql_executor = stores.sql_executor
    table_schemas = {
        key: [str(column) for column in value]
        for key, value in structured_raw.get("table_schemas", {}).items()
        if isinstance(value, list)
    }
    table_aliases = {str(alias): str(target) for alias, target in structured_raw.get("table_aliases", {}).items()}
    template_engine = QueryTemplateEngine(
        templates=structured_raw.get("templates"),
        table_schemas=table_schemas,
        table_aliases=table_aliases,
        default_table=str(structured_raw.get("default_table", "documents")),
    )
    structured_service = StructuredRetrievalService(
        sql_generator=SafeSQLGenerator(
            allowed_tables=[str(table) for table in structured_raw.get("allowed_tables", list(table_schemas.keys()))],
            table_schemas=table_schemas,
        ),
        db_connection=sql_executor,
        result_formatter=StructuredResultFormatter(),
        template_engine=template_engine,
    )

    routed_flow = RoutedQueryFlow(
        router=router_service,
        injection_guard=injection_guard,
        scope_validator=scope_validator,
        fallback_handler=fallback_handler,
        standard_flow=answer_runtime.answer_flow,
        structured_service=structured_service,
        comparative_decomposer=ComparativeDecomposer(),
        two_hop_decomposer=TwoHopDecomposer(),
        aggregator=SubAnswerAggregator(answer_runtime.answer_flow.generation_service),
        output_guard=output_guard,
    )
    return QueryRuntime(flow=routed_flow, classifier=classifier, output_guard=output_guard)


def _get_or_build_query_classifier(request: Request) -> QueryClassifier:
    """Return a cached classifier without requiring the full routed runtime."""
    classifier = getattr(request.app.state, "query_classifier", None)
    if classifier is not None:
        return classifier
    classifier = QueryClassifier()
    request.app.state.query_classifier = classifier
    return classifier


def _parse_route_type(value: object) -> RouteType:
    """Coerce config values into a valid route type with a safe default."""
    if isinstance(value, RouteType):
        return value
    if isinstance(value, str):
        try:
            return RouteType(value)
        except ValueError:
            return RouteType.STANDARD
    return RouteType.STANDARD
