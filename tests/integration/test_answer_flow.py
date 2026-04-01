"""Integration tests for the Phase 4 answer flow and API."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from types import SimpleNamespace
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.routes.answer import router as answer_router
from apps.api.routes.providers import router as providers_router
from src.layer0_core.errors import ProviderError
from src.layer1_contracts.schemas.chunk import Chunk, ChunkLocation, ChunkMetadata
from src.layer1_contracts.schemas.health import HealthStatus, ProviderHealth
from src.layer1_contracts.schemas.llm import LLMConfig, LLMRequest, Message, MessageRole
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.retrieval_config import RetrievalConfig
from src.layer2_domain.citations.extractor import CitationExtractor
from src.layer2_domain.citations.validator import CitationValidator
from src.layer2_domain.evidence.orderer import EvidenceOrderer
from src.layer2_domain.evidence.selector import EvidenceSelector
from src.layer2_domain.evidence.service import EvidenceService
from src.layer2_domain.evidence.windower import ContextWindowManager
from src.layer2_domain.failover.service import FailoverService
from src.layer2_domain.failover.state_machine import FailoverConfig
from src.layer2_domain.generation.abstention import AbstentionChecker
from src.layer2_domain.generation.grounding import GroundingValidator
from src.layer2_domain.generation.prompt_builder import PromptBuilder
from src.layer2_domain.generation.service import GenerationService
from src.layer2_domain.indexing.service import IndexingService
from src.layer2_domain.reranking.service import RerankingService
from src.layer2_domain.retrieval.dense_retriever import DenseRetriever
from src.layer2_domain.retrieval.diagnostics import RetrievalDiagnosticsStore
from src.layer2_domain.retrieval.deduplication import CandidateDeduplicator
from src.layer2_domain.retrieval.filters.freshness_filter import FreshnessBooster
from src.layer2_domain.retrieval.filters.metadata_filter import MetadataFilter
from src.layer2_domain.retrieval.filters.trust_filter import TrustFilter
from src.layer2_domain.retrieval.hybrid_orchestrator import HybridOrchestrator
from src.layer2_domain.retrieval.lexical_retriever import LexicalRetriever
from src.layer2_domain.retrieval.service import RetrievalService
from src.layer3_flows.answer_flow.flow import AnswerFlow
from src.layer4_providers.embeddings.mock.adapter import MockEmbedder
from src.layer4_providers.llms.base import BaseLLMProvider
from src.layer4_providers.llms.mock.provider import MockLLMProvider
from src.layer4_providers.llms.openai.adapter import OpenAIProvider
from src.layer4_providers.llms.anthropic.adapter import AnthropicProvider
from src.layer4_providers.llms.google.adapter import GoogleProvider
from src.layer4_providers.llms.groq.adapter import GroqProvider
from src.layer4_providers.rerankers.mock.adapter import MockReranker
from src.layer4_providers.stores.metadata.sqlite_adapter import SQLiteMetadataStore
from src.layer4_providers.stores.qdrant.adapter import QdrantAdapter
from src.layer4_providers.stores.sqlite_fts.adapter import SQLiteFTSAdapter


async def _build_answer_flow(tmp_path) -> AnswerFlow:
    embedder = MockEmbedder(dimensions=32)
    vector_store = QdrantAdapter(
        url="memory://",
        collection=f"answer_{uuid.uuid4().hex[:8]}",
        dimensions=embedder.dimensions,
    )
    lexical_store = SQLiteFTSAdapter(db_path=str(tmp_path / "lexical.db"))
    metadata_store = SQLiteMetadataStore(db_path=str(tmp_path / "metadata.db"))
    indexing_service = IndexingService(
        embedder=embedder,
        vector_store=vector_store,
        lexical_store=lexical_store,
        metadata_store=metadata_store,
    )
    now = datetime.now(timezone.utc)
    chunks = [
        Chunk(
            id="chunk-answer-1",
            document_id="doc-answer-1",
            content="Hybrid retrieval combines dense vectors and lexical BM25 search with fusion.",
            location=ChunkLocation(start_char=0, end_char=77),
            sequence_number=0,
            metadata=ChunkMetadata(
                document_title="Retrieval Guide",
                document_type="md",
                tags=["retrieval"],
                trust_score=0.95,
                section_title="Hybrid Retrieval",
                page_numbers=[1],
            ),
            created_at=now,
        )
    ]
    await indexing_service.index_chunks(chunks, document_checksum="answer-flow")

    retrieval_service = RetrievalService(
        orchestrator=HybridOrchestrator(
            dense_retriever=DenseRetriever(embedder, vector_store, metadata_store),
            lexical_retriever=LexicalRetriever(lexical_store, metadata_store),
            reranking_service=RerankingService(MockReranker()),
            metadata_filter=MetadataFilter(metadata_store),
            freshness_booster=FreshnessBooster(),
            deduplicator=CandidateDeduplicator(),
            diagnostics_store=RetrievalDiagnosticsStore(),
            metadata_store=metadata_store,
            trust_filter=TrustFilter(metadata_store),
        ),
        default_config=RetrievalConfig(final_top_k=2, rerank_top_k=2),
    )
    evidence_service = EvidenceService(
        selector=EvidenceSelector(),
        windower=ContextWindowManager(),
        orderer=EvidenceOrderer(),
    )
    generation_service = GenerationService(
        failover_service=FailoverService(
            providers=[
                MockLLMProvider(
                    provider_id="mock-primary",
                    model="mock-model",
                    response_template="Hybrid retrieval combines dense vectors and lexical BM25 search [1].",
                    random_func=lambda: 0.9,
                    sleep_func=_fake_sleep,
                )
            ],
            config=FailoverConfig(),
        ),
        prompt_builder=PromptBuilder(),
        citation_extractor=CitationExtractor(),
        citation_validator=CitationValidator(),
        abstention_checker=AbstentionChecker(),
        grounding_validator=GroundingValidator(),
        default_model="mock-model",
    )
    return AnswerFlow(
        retrieval_service=retrieval_service,
        evidence_service=evidence_service,
        generation_service=generation_service,
    )


@pytest.mark.asyncio
async def test_answer_flow_generates_grounded_answer_and_trace(tmp_path) -> None:
    """End-to-end answer flow should produce a cited answer and trace."""
    flow = await _build_answer_flow(tmp_path)

    answer, trace = await flow.execute(Query(id="query-1", text="hybrid retrieval"))

    assert answer.status == "success"
    assert answer.citations
    assert answer.citations[0].citation_key == "[1]"
    assert answer.evidence_item_ids == ["chunk-answer-1"]
    assert trace.request_id == "query-1"
    assert trace.provider_used == "mock-primary"
    assert trace.evidence_items == ["chunk-answer-1"]


@pytest.mark.asyncio
async def test_answer_api_exposes_answer_and_trace(tmp_path) -> None:
    """The answer API should return answers and cache traces."""
    app = FastAPI()
    app.include_router(answer_router, prefix="/answer")
    app.state.answer_flow = await _build_answer_flow(tmp_path)
    app.state.answer_trace_store = {}

    with TestClient(app) as client:
        response = client.post(
            "/answer",
            json={
                "query": "hybrid retrieval",
                "top_k": 2,
                "max_evidence": 2,
                "include_trace": True,
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "success"
        assert payload["citations"][0]["citation_key"] == "[1]"
        assert payload["trace"]["provider_used"] == "mock-primary"

        trace = client.get(f"/answer/trace/{payload['query_id']}")
        assert trace.status_code == 200
        assert trace.json()["request_id"] == payload["query_id"]


def test_answer_api_requires_real_provider_runtime_when_not_injected(monkeypatch) -> None:
    """The default answer route should not silently fall back to mock startup providers."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    app = FastAPI()
    app.include_router(answer_router, prefix="/answer")

    with TestClient(app) as client:
        response = client.post("/answer", json={"query": "hybrid retrieval"})
        assert response.status_code == 503
        assert "real LLM providers" in response.json()["detail"]


def test_provider_routes_do_not_fallback_to_startup_registry(monkeypatch) -> None:
    """Provider routes should not fall back to startup providers when Phase 4 runtime is unavailable."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    class _StartupRegistry:
        async def refresh_all_health(self) -> dict[str, ProviderHealth]:
            return {
                "startup-mock": ProviderHealth(
                    provider_id="startup-mock",
                    provider_type="llm",
                    vendor="mock",
                    status=HealthStatus.HEALTHY,
                )
            }

    app = FastAPI()
    app.include_router(providers_router, prefix="/providers")
    app.state.startup_result = SimpleNamespace(
        provider_registry=_StartupRegistry(),
        failover_service=None,
    )

    with TestClient(app) as client:
        response = client.get("/providers/health")
        assert response.status_code == 200
        assert response.json() == []


def test_provider_errors_mask_api_keys() -> None:
    """Provider error messages should redact secrets before surfacing."""
    provider = _InspectableProvider(api_key="sk-this-should-not-leak-1234567890")

    with pytest.raises(ProviderError) as exc_info:
        provider._handle_error(400, {"error": {"message": "Authorization=Bearer sk-this-should-not-leak-1234567890"}}, "Inspectable")

    message = str(exc_info.value)
    assert "sk-this-should-not-leak-1234567890" not in message
    assert "***REDACTED***" in message


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not configured")
@pytest.mark.asyncio
async def test_openai_provider_real_api_smoke() -> None:
    """OpenAI adapter should complete a minimal real request when credentials exist."""
    provider = OpenAIProvider(model="gpt-4o-mini")
    response = await provider.complete(_live_request("Say the word vector."))

    assert response.content
    assert response.provider == "openai"


@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not configured")
@pytest.mark.asyncio
async def test_anthropic_provider_real_api_smoke() -> None:
    """Anthropic adapter should complete a minimal real request when credentials exist."""
    provider = AnthropicProvider(model="claude-3-haiku-20240307")
    response = await provider.complete(_live_request("Say the word vector."))

    assert response.content
    assert response.provider == "anthropic"


@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="GROQ_API_KEY not configured")
@pytest.mark.asyncio
async def test_groq_provider_real_api_smoke() -> None:
    """Groq adapter should complete a minimal real request when credentials exist."""
    provider = GroqProvider(model="llama-3.1-70b-versatile")
    response = await provider.complete(_live_request("Say the word vector."))

    assert response.content
    assert response.provider == "groq"


@pytest.mark.asyncio
async def test_real_provider_failover_smoke_when_credentials_exist(monkeypatch) -> None:
    """Failover should move from a failing real adapter to a working real adapter when possible."""
    backup = _build_real_backup_provider()
    if backup is None:
        pytest.skip("No real provider credentials available for failover smoke test")

    failing_primary = OpenAIProvider(provider_id="openai-invalid", api_key="sk-invalid", model="gpt-4o-mini")
    service = FailoverService(
        providers=[failing_primary, backup],
        config=FailoverConfig(max_retries=0, base_delay_seconds=0.0, jitter=False),
    )

    response = await service.execute(_live_request("Say the word vector."))

    assert response.content
    assert response.provider == backup.provider_id
    assert response.failover_occurred is True


async def _fake_sleep(_: float) -> None:
    """Async no-op for provider tests."""


def _live_request(prompt: str) -> LLMRequest:
    """Build a minimal live-provider request."""
    return LLMRequest(
        id=f"live-{uuid.uuid4().hex[:8]}",
        messages=[Message(role=MessageRole.USER, content=prompt)],
        config=LLMConfig(model="placeholder-model", temperature=0.0, max_tokens=16),
        timeout_seconds=30.0,
    )


def _build_real_backup_provider():
    """Return any configured real provider for smoke failover tests."""
    if os.getenv("GROQ_API_KEY"):
        return GroqProvider(provider_id="groq-backup", model="llama-3.1-70b-versatile")
    if os.getenv("OPENAI_API_KEY"):
        return OpenAIProvider(provider_id="openai-backup", model="gpt-4o-mini")
    if os.getenv("ANTHROPIC_API_KEY"):
        return AnthropicProvider(provider_id="anthropic-backup", model="claude-3-haiku-20240307")
    if os.getenv("GOOGLE_API_KEY"):
        return GoogleProvider(provider_id="google-backup", model="gemini-1.5-pro")
    return None


class _InspectableProvider(BaseLLMProvider):
    """Small test-only provider to exercise masking behavior."""

    def __init__(self, api_key: str) -> None:
        super().__init__(
            provider_id="inspectable",
            api_key=api_key,
            base_url="https://example.invalid",
            model="inspectable-model",
        )

    @property
    def vendor(self) -> str:
        return "inspectable"

    async def complete(self, request: LLMRequest):
        raise NotImplementedError
