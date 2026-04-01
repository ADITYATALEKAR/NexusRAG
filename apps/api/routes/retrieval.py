"""Retrieval and diagnostics routes."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field

from apps.api.runtime_storage import load_storage_runtime
from src.layer0_core.ids.base import QueryId
from src.layer1_contracts.schemas.query import Query, QueryConfig, QueryFilters
from src.layer1_contracts.schemas.retrieval import RetrievalCandidate, RetrievalDiagnostics
from src.layer1_contracts.schemas.retrieval_config import (
    FilterConfig,
    FusionMethod,
    RetrievalConfig,
    RetrievalMode,
)
from src.layer2_domain.reranking.service import RerankingService
from src.layer2_domain.compression.quantizer import ProductQuantizer, ScalarQuantizer
from src.layer2_domain.graph_retrieval.graph_builder import DocumentGraphBuilder
from src.layer2_domain.graph_retrieval.service import GraphRetrievalService
from src.layer2_domain.query_understanding.entity_extractor import EntityExtractor
from src.layer2_domain.retrieval.dense_retriever import DenseRetriever
from src.layer2_domain.retrieval.diagnostics import RetrievalDiagnosticsStore
from src.layer2_domain.retrieval.deduplication import CandidateDeduplicator
from src.layer2_domain.retrieval.filters.freshness_filter import FreshnessBooster
from src.layer2_domain.retrieval.filters.metadata_filter import MetadataFilter
from src.layer2_domain.retrieval.filters.trust_filter import TrustFilter
from src.layer2_domain.retrieval.hybrid_orchestrator import HybridOrchestrator
from src.layer2_domain.retrieval.lexical_retriever import LexicalRetriever
from src.layer2_domain.retrieval.service import RetrievalService
from src.layer3_flows.retrieval_flow.flow import RetrievalFlow
from src.layer4_providers.embeddings.mock.adapter import MockEmbedder
from src.layer4_providers.rerankers.registry import build_reranker
from src.layer4_providers.stores.graph.networkx_adapter import NetworkXGraphStore
from src.layer4_providers.stores.metadata.sqlite_adapter import SQLiteMetadataStore
from src.layer4_providers.stores.qdrant.adapter import QdrantAdapter
from src.layer4_providers.stores.sqlite_fts.adapter import SQLiteFTSAdapter
from src.layer8_runtime.config.loader import ConfigLoader
from src.layer8_runtime.feature_flags.manager import FeatureFlagManager

router = APIRouter()


class RetrievalRequest(BaseModel):
    """API request body for retrieval."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(..., min_length=1)
    top_k: int = Field(default=10, ge=1, le=100)
    mode: RetrievalMode = RetrievalMode.HYBRID
    rerank: bool = True
    filters: FilterConfig | None = None
    include_diagnostics: bool = False


class RetrievalResponse(BaseModel):
    """API response body for retrieval."""

    model_config = ConfigDict(extra="forbid")

    query_id: str
    candidates: list[RetrievalCandidate]
    total: int
    latency_ms: int
    diagnostics: RetrievalDiagnostics | None = None


@router.post("/retrieve", response_model=RetrievalResponse)
async def retrieve(
    payload: RetrievalRequest,
    request: Request,
) -> RetrievalResponse:
    """Run retrieval and optionally include stage diagnostics."""
    retrieval_service = _get_or_build_retrieval_service(request)
    query = Query(
        id=QueryId.generate().value,
        text=payload.query,
        filters=_build_query_filters(payload.filters),
        config=QueryConfig(
            top_k=payload.top_k,
            rerank=payload.rerank,
            rerank_top_k=max(payload.top_k, retrieval_service.default_config.rerank_top_k),
        ),
    )
    config = retrieval_service.default_config.model_copy(deep=True)
    config.mode = payload.mode
    config.final_top_k = payload.top_k
    config.rerank_enabled = payload.rerank
    config.rerank_top_k = max(payload.top_k, config.rerank_top_k)

    result = await retrieval_service.retrieve(query, config)
    return RetrievalResponse(
        query_id=result.query_id,
        candidates=result.candidates,
        total=len(result.candidates),
        latency_ms=result.total_latency_ms,
        diagnostics=result.diagnostics if payload.include_diagnostics else None,
    )


@router.get("/diagnostics/{query_id}", response_model=RetrievalDiagnostics)
async def get_diagnostics(
    query_id: str,
    request: Request,
) -> RetrievalDiagnostics:
    """Return cached diagnostics for a previous retrieval."""
    retrieval_service = _get_or_build_retrieval_service(request)
    diagnostics = retrieval_service.get_diagnostics(query_id)
    if diagnostics is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnostics not found")
    return diagnostics


def _build_query_filters(filters: FilterConfig | None) -> QueryFilters:
    """Convert API filters to the query contract."""
    if filters is None:
        return QueryFilters()
    return QueryFilters(
        document_ids=filters.document_ids,
        document_types=filters.document_types,
        tags=filters.tags,
        date_from=_parse_iso_datetime(filters.date_from),
        date_to=_parse_iso_datetime(filters.date_to),
        min_trust_score=filters.min_trust_score,
        exclude_chunk_ids=filters.exclude_chunk_ids,
    )


def _parse_iso_datetime(value: str | None) -> datetime | None:
    """Parse ISO datetimes from API filters."""
    if value is None:
        return None
    return datetime.fromisoformat(value)


def _get_or_build_retrieval_service(request: Request) -> RetrievalService:
    """Return the cached retrieval service or lazily construct it."""
    retrieval_service = getattr(request.app.state, "retrieval_service", None)
    if retrieval_service is not None:
        return retrieval_service
    retrieval_service, retrieval_flow = _build_retrieval_stack()
    request.app.state.retrieval_service = retrieval_service
    request.app.state.retrieval_flow = retrieval_flow
    return retrieval_service


def _build_retrieval_stack(config_dir: Path | None = None) -> tuple[RetrievalService, RetrievalFlow]:
    """Build the retrieval stack for the API, including Phase 6 feature flags."""
    resolved_config_dir = config_dir or Path(__file__).resolve().parents[3] / "configs"
    loader = ConfigLoader(config_dir=resolved_config_dir)
    retrieval_raw = loader.load_yaml("retrieval/retrieval.yaml").get("retrieval", {})
    fusion_raw = loader.load_yaml("retrieval/fusion.yaml").get("fusion", {})
    reranking_raw = loader.load_yaml("retrieval/reranking.yaml").get("reranking", {})
    feature_flag_raw = loader.load_yaml("feature_flags.yaml")
    graph_raw = loader.load_yaml("advanced/graph.yaml")
    compression_raw = loader.load_yaml("advanced/compression.yaml")

    project_root = resolved_config_dir.parent
    storage = load_storage_runtime(project_root=project_root)

    feature_flags = FeatureFlagManager()
    feature_flags.load_from_mapping(feature_flag_raw)
    compression_quantizer = _build_compression_quantizer(
        compression_raw,
        storage.vector_compression_state_path,
    )

    embedder = MockEmbedder(dimensions=32)
    metadata_store = SQLiteMetadataStore(db_path=str(storage.metadata_db_path))
    vector_store = QdrantAdapter(
        url=storage.qdrant_url,
        api_key=storage.qdrant_api_key,
        collection=storage.qdrant_collection,
        dimensions=embedder.dimensions,
    )
    lexical_store = SQLiteFTSAdapter(db_path=str(storage.lexical_db_path))
    reranker = build_reranker(provider=reranking_raw.get("provider", "mock"))
    diagnostics_store = RetrievalDiagnosticsStore()

    default_config = RetrievalConfig(
        mode=RetrievalMode(retrieval_raw.get("default_mode", "hybrid")),
        dense_top_k=int(retrieval_raw.get("dense_top_k", 50)),
        lexical_top_k=int(retrieval_raw.get("lexical_top_k", 50)),
        fusion_top_k=int(retrieval_raw.get("fusion_top_k", 25)),
        final_top_k=int(retrieval_raw.get("final_top_k", 10)),
        min_score_threshold=retrieval_raw.get("min_score_threshold"),
        fusion_method=FusionMethod(fusion_raw.get("method", "rrf")),
        rrf_k=int(fusion_raw.get("rrf_k", 60)),
        dense_weight=float(fusion_raw.get("dense_weight", 0.5)),
        lexical_weight=float(fusion_raw.get("lexical_weight", 0.5)),
        rerank_enabled=bool(reranking_raw.get("enabled", True)),
        rerank_top_k=int(reranking_raw.get("top_k", 25)),
    )

    orchestrator = HybridOrchestrator(
        dense_retriever=DenseRetriever(
            embedder=embedder,
            vector_store=vector_store,
            metadata_store=metadata_store,
            feature_flags=feature_flags,
            compression_quantizer=compression_quantizer,
        ),
        lexical_retriever=LexicalRetriever(lexical_store=lexical_store, metadata_store=metadata_store),
        reranking_service=RerankingService(reranker=reranker),
        metadata_filter=MetadataFilter(metadata_store=metadata_store),
        freshness_booster=FreshnessBooster(decay_days=int(retrieval_raw.get("freshness_decay_days", 30))),
        deduplicator=CandidateDeduplicator(),
        diagnostics_store=diagnostics_store,
        metadata_store=metadata_store,
        trust_filter=TrustFilter(metadata_store=metadata_store),
    )
    graph_service = GraphRetrievalService(
        graph_builder=DocumentGraphBuilder(EntityExtractor()),
        feature_flags=feature_flags,
        standard_retrieval=orchestrator,
        entity_extractor=EntityExtractor(),
        graph_boost=float(graph_raw.get("boost_factor", 0.15)),
        graph_store=NetworkXGraphStore(path=str(storage.graph_path)),
    )
    graph_service.build_graph(metadata_store.list_documents_sync(), metadata_store.list_chunks_sync())
    retrieval_service = RetrievalService(orchestrator=graph_service, default_config=default_config)
    retrieval_flow = RetrievalFlow(retrieval_service=retrieval_service)
    return retrieval_service, retrieval_flow


def _build_compression_quantizer(config: dict, state_path: Path) -> object | None:
    """Return a compression quantizer initialized from config and persisted state."""
    method = config.get("default_method", "scalar")
    if method == "scalar":
        scalar_config = config.get("scalar", {})
        if not scalar_config.get("enabled", True):
            return None
        if state_path.exists():
            return ScalarQuantizer.load(state_path)
        return ScalarQuantizer()

    product_config = config.get("product_quantization", {})
    if state_path.exists():
        return ProductQuantizer.load(state_path)
    return ProductQuantizer(
        num_subvectors=int(product_config.get("num_subvectors", 8)),
        num_centroids=int(product_config.get("num_centroids", 256)),
    )
