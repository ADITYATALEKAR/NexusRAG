"""Answer generation routes."""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from apps.api.public_demo import (
    PublicDemoUsageTracker,
    TrialUsage,
    build_quota_message,
    public_query_limit,
    resolve_session_id,
    should_enforce_public_demo_limit,
)
from apps.api.routes.retrieval import _get_or_build_retrieval_service
from src.layer0_core.ids.base import QueryId
from src.layer1_contracts.schemas.answer import AnswerStatus, Citation
from src.layer1_contracts.schemas.evidence import EvidenceConfig
from src.layer1_contracts.schemas.generation import GenerationConfig, GenerationTrace
from src.layer1_contracts.schemas.query import Query, QueryConfig
from src.layer1_contracts.schemas.retrieval_config import RetrievalConfig
from src.layer2_domain.citations.extractor import CitationExtractor
from src.layer2_domain.citations.validator import CitationValidator
from src.layer2_domain.evidence.orderer import EvidenceOrderer
from src.layer2_domain.evidence.selector import EvidenceSelector
from src.layer2_domain.evidence.service import EvidenceService
from src.layer2_domain.evidence.windower import ContextWindowManager
from src.layer2_domain.failover.service import FailoverService
from src.layer2_domain.failover.state_machine import FailoverConfig as DomainFailoverConfig
from src.layer2_domain.generation.abstention import AbstentionChecker
from src.layer2_domain.generation.grounding import GroundingValidator
from src.layer2_domain.generation.prompt_builder import PromptBuilder
from src.layer2_domain.generation.service import GenerationService
from src.layer3_flows.answer_flow.flow import AnswerFlow
from src.layer4_providers.llms.registry import build_configured_providers, load_provider_config
from src.layer5_wiring.observability.cost_tracker import cost_tracker
from src.layer5_wiring.observability.logging import logger
from src.layer5_wiring.registry.provider_registry import ProviderRegistry
from src.layer8_runtime.config.loader import ConfigLoader
from src.layer8_runtime.config.schemas import FailoverFileConfig

router = APIRouter()


class AnswerRequest(BaseModel):
    """API request body for answer generation."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(..., min_length=1)
    top_k: int = Field(default=10, ge=1, le=100)
    max_evidence: int = Field(default=5, ge=1, le=20)
    model: str | None = None
    require_citations: bool = True
    include_trace: bool = False


class AnswerResponse(BaseModel):
    """API response body for answer generation."""

    model_config = ConfigDict(extra="forbid")

    answer_id: str
    query_id: str
    text: str
    status: AnswerStatus
    citations: list[Citation]
    trace: GenerationTrace | None = None


@dataclass
class AnswerRuntime:
    """Lazily constructed runtime for the answer pipeline."""

    answer_flow: AnswerFlow
    provider_registry: ProviderRegistry
    failover_service: FailoverService
    trace_store: dict[str, GenerationTrace] = field(default_factory=dict)
    default_retrieval_config: RetrievalConfig = field(default_factory=RetrievalConfig)
    default_evidence_config: EvidenceConfig = field(default_factory=EvidenceConfig)
    default_generation_config: GenerationConfig = field(default_factory=GenerationConfig)


@router.post("", response_model=AnswerResponse)
async def generate_answer(payload: AnswerRequest, request: Request, response: Response) -> AnswerResponse | JSONResponse:
    """Generate a grounded answer for a user query."""
    trial_usage = _consume_public_demo_quota(request)
    if trial_usage is not None and not trial_usage.allowed:
        quota_headers = _build_trial_headers(trial_usage)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "message": build_quota_message(trial_usage.limit),
                "trial_limit": trial_usage.limit,
                "trial_used": trial_usage.used,
                "trial_remaining": trial_usage.remaining,
            },
            headers=quota_headers,
        )

    runtime = await _get_or_build_answer_runtime(request)
    query = Query(
        id=QueryId.generate().value,
        text=payload.query,
        request_id=getattr(request.state, "request_id", None),
        config=QueryConfig(top_k=payload.top_k, rerank_top_k=max(payload.top_k, 25)),
    )
    answer, trace = await runtime.answer_flow.execute(
        query=query,
        retrieval_config=runtime.default_retrieval_config.model_copy(
            update={
                "final_top_k": payload.top_k,
                "rerank_top_k": max(payload.top_k, runtime.default_retrieval_config.rerank_top_k),
            }
        ),
        evidence_config=runtime.default_evidence_config.model_copy(
            update={"max_evidence_items": payload.max_evidence}
        ),
        generation_config=runtime.default_generation_config.model_copy(
            update={
                "model": payload.model or runtime.default_generation_config.model,
                "require_citations": payload.require_citations,
            }
        ),
    )
    runtime.trace_store[trace.request_id] = trace
    request.app.state.answer_trace_store = runtime.trace_store
    tracked_request_id = getattr(request.state, "request_id", None) or trace.request_id
    cost_tracker.record(
        request_id=tracked_request_id,
        provider=trace.provider_used,
        model=trace.model_used,
        prompt_tokens=trace.prompt_tokens,
        completion_tokens=trace.completion_tokens,
    )
    logger.log_provider_call(
        provider=trace.provider_used,
        model=trace.model_used,
        tokens=trace.prompt_tokens + trace.completion_tokens,
        latency_ms=trace.latency_ms,
        success=answer.status != AnswerStatus.FAILED,
    )
    if trial_usage is not None:
        for header_name, header_value in _build_trial_headers(trial_usage).items():
            response.headers[header_name] = header_value
    return AnswerResponse(
        answer_id=answer.id,
        query_id=answer.query_id,
        text=answer.text,
        status=answer.status,
        citations=answer.citations,
        trace=trace if payload.include_trace else None,
    )


@router.get("/trace/{request_id}", response_model=GenerationTrace)
async def get_trace(request_id: str, request: Request) -> GenerationTrace:
    """Return a cached answer trace by request identifier."""
    runtime = await _get_or_build_answer_runtime(request)
    trace = runtime.trace_store.get(request_id)
    if trace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trace not found")
    return trace


async def _get_or_build_answer_runtime(request: Request) -> AnswerRuntime:
    """Return the cached answer runtime or lazily construct it."""
    runtime = getattr(request.app.state, "answer_runtime", None)
    if runtime is not None:
        return runtime

    if hasattr(request.app.state, "answer_flow"):
        existing_runtime = AnswerRuntime(
            answer_flow=request.app.state.answer_flow,
            provider_registry=getattr(request.app.state, "answer_provider_registry", ProviderRegistry()),
            failover_service=getattr(
                request.app.state,
                "answer_failover_service",
                getattr(
                    getattr(request.app.state, "startup_result", None),
                    "failover_service",
                    FailoverService([], DomainFailoverConfig()),
                ),
            ),
            trace_store=getattr(request.app.state, "answer_trace_store", {}),
        )
        request.app.state.answer_runtime = existing_runtime
        return existing_runtime

    runtime = await _build_answer_runtime(request)
    request.app.state.answer_runtime = runtime
    request.app.state.answer_flow = runtime.answer_flow
    request.app.state.answer_provider_registry = runtime.provider_registry
    request.app.state.answer_failover_service = runtime.failover_service
    request.app.state.answer_trace_store = runtime.trace_store
    return runtime


async def _build_answer_runtime(request: Request) -> AnswerRuntime:
    """Construct the Phase 4 answer runtime from config and existing services."""
    config_dir = Path(__file__).resolve().parents[3] / "configs"
    loader = ConfigLoader(config_dir=config_dir)
    generation_raw = loader.load_yaml("generation/generation.yaml").get("generation", {})
    prompts_raw = loader.load_yaml("generation/prompts.yaml").get("prompts", {})
    abstention_raw = loader.load_yaml("generation/abstention.yaml").get("abstention", {})
    provider_raw = load_provider_config(config_dir)
    failover_file_config = loader.load_validated("models/llm-failover.yaml", FailoverFileConfig, apply_env_overrides=False)

    provider_registry = ProviderRegistry()
    providers = build_configured_providers(provider_raw)
    if not providers:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No configured real LLM providers are available for the answer runtime",
        )
    retrieval_service = _get_or_build_retrieval_service(request)
    for provider in providers:
        await provider_registry.register(provider, check_health=False)
    failover_service = FailoverService(
        providers=provider_registry.get_all(),
        config=DomainFailoverConfig(
            max_retries=failover_file_config.failover.retry.max_retries,
            base_delay_seconds=failover_file_config.failover.retry.base_delay_seconds,
            max_delay_seconds=failover_file_config.failover.retry.max_delay_seconds,
            backoff_multiplier=failover_file_config.failover.retry.backoff_multiplier,
            jitter=failover_file_config.failover.retry.jitter,
            cooldown_duration_seconds=failover_file_config.failover.cooldown.default_duration_seconds,
            max_cooldown_duration_seconds=failover_file_config.failover.cooldown.max_duration_seconds,
            consecutive_failures_threshold=failover_file_config.failover.cooldown.consecutive_failures_threshold,
        ),
    )

    prompt_builder = PromptBuilder(
        default_system_prompt=prompts_raw.get("system_prompt"),
        evidence_template=prompts_raw.get("evidence_template"),
        user_template=prompts_raw.get("user_template"),
        abstention_template=prompts_raw.get("abstention_template"),
    )
    evidence_service = EvidenceService(
        selector=EvidenceSelector(),
        windower=ContextWindowManager(),
        orderer=EvidenceOrderer(),
    )
    generation_service = GenerationService(
        failover_service=failover_service,
        prompt_builder=prompt_builder,
        citation_extractor=CitationExtractor(),
        citation_validator=CitationValidator(),
        abstention_checker=AbstentionChecker(
            min_evidence_items=int(abstention_raw.get("min_evidence_items", 1)),
            min_relevance_score=float(abstention_raw.get("min_relevance_score", 0.3)),
            min_avg_relevance=float(abstention_raw.get("min_avg_relevance", 0.4)),
        ),
        grounding_validator=GroundingValidator(),
        default_model=str(generation_raw.get("default_model", "gpt-4o")),
    )
    answer_flow = AnswerFlow(
        retrieval_service=retrieval_service,
        evidence_service=evidence_service,
        generation_service=generation_service,
    )
    return AnswerRuntime(
        answer_flow=answer_flow,
        provider_registry=provider_registry,
        failover_service=failover_service,
        default_retrieval_config=retrieval_service.default_config.model_copy(deep=True),
        default_evidence_config=EvidenceConfig(),
        default_generation_config=GenerationConfig(
            model=str(generation_raw.get("default_model", "gpt-4o")),
            temperature=float(generation_raw.get("temperature", 0.1)),
            max_output_tokens=int(generation_raw.get("max_output_tokens", 1024)),
            require_citations=bool(generation_raw.get("require_citations", True)),
            allow_abstention=bool(generation_raw.get("allow_abstention", True)),
            grounding_threshold=float(generation_raw.get("grounding_threshold", 0.5)),
        ),
    )


def _consume_public_demo_quota(request: Request) -> TrialUsage | None:
    """Consume one hosted-trial query when public demo mode is active."""
    if not should_enforce_public_demo_limit(request):
        return None

    tracker = _get_or_build_public_demo_tracker(request)
    return tracker.consume(resolve_session_id(request))


def _get_or_build_public_demo_tracker(request: Request) -> PublicDemoUsageTracker:
    """Return the cached public demo tracker or create it from env."""
    tracker = getattr(request.app.state, "public_demo_tracker", None)
    if tracker is not None:
        return tracker

    storage_runtime = getattr(request.app.state, "storage_runtime", None)
    database_url = getattr(storage_runtime, "database_url", None)
    if database_url is None:
        database_url = (
            os.getenv("DATABASE_URL")
            or os.getenv("NEON_DATABASE_URL")
            or os.getenv("NEXUSRAG_DATABASE_URL")
        )
    tracker = PublicDemoUsageTracker(
        database_url=database_url,
        limit=public_query_limit(),
    )
    request.app.state.public_demo_tracker = tracker
    return tracker


def _build_trial_headers(usage: TrialUsage) -> dict[str, str]:
    """Serialize trial usage into response headers."""
    return {
        "X-NexusRAG-Trial-Limit": str(usage.limit),
        "X-NexusRAG-Trial-Used": str(usage.used),
        "X-NexusRAG-Trial-Remaining": str(usage.remaining),
    }
