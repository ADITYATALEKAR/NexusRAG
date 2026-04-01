"""Hybrid retrieval orchestration."""

from __future__ import annotations

import time

from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.retrieval import (
    HybridRetrievalResult,
    RetrievalCandidate,
    RetrievalDiagnostics,
    RetrievalSource,
    RetrievalStageResult,
)
from src.layer1_contracts.schemas.retrieval_config import (
    FilterConfig,
    FusionMethod,
    RetrievalConfig,
    RetrievalMode,
)
from src.layer1_contracts.interfaces.metadata_store import MetadataStoreInterface
from src.layer2_domain.reranking.service import RerankingService
from src.layer2_domain.retrieval.dense_retriever import DenseRetriever
from src.layer2_domain.retrieval.diagnostics import RetrievalDiagnosticsStore
from src.layer2_domain.retrieval.deduplication import CandidateDeduplicator
from src.layer2_domain.retrieval.filters.freshness_filter import FreshnessBooster
from src.layer2_domain.retrieval.filters.metadata_filter import MetadataFilter
from src.layer2_domain.retrieval.filters.trust_filter import TrustFilter
from src.layer2_domain.retrieval.fusion.base import FusionStrategy
from src.layer2_domain.retrieval.fusion.rrf import ReciprocalRankFusion
from src.layer2_domain.retrieval.fusion.weighted import WeightedScoreFusion
from src.layer2_domain.retrieval.lexical_retriever import LexicalRetriever
class HybridOrchestrator:
    """Orchestrate dense retrieval, lexical retrieval, fusion, filtering, and reranking."""

    FUSION_STRATEGIES: dict[FusionMethod, type[FusionStrategy]] = {
        FusionMethod.RRF: ReciprocalRankFusion,
        FusionMethod.WEIGHTED: WeightedScoreFusion,
    }

    def __init__(
        self,
        dense_retriever: DenseRetriever,
        lexical_retriever: LexicalRetriever,
        reranking_service: RerankingService,
        metadata_filter: MetadataFilter,
        freshness_booster: FreshnessBooster,
        deduplicator: CandidateDeduplicator,
        diagnostics_store: RetrievalDiagnosticsStore | None = None,
        metadata_store: MetadataStoreInterface | None = None,
        trust_filter: TrustFilter | None = None,
    ) -> None:
        self.dense_retriever = dense_retriever
        self.lexical_retriever = lexical_retriever
        self.reranking_service = reranking_service
        self.metadata_filter = metadata_filter
        self.freshness_booster = freshness_booster
        self.deduplicator = deduplicator
        self.diagnostics_store = diagnostics_store or RetrievalDiagnosticsStore()
        self.metadata_store = metadata_store or dense_retriever.metadata_store
        self.trust_filter = trust_filter or TrustFilter(self.metadata_store)

    async def retrieve(
        self,
        query: Query,
        config: RetrievalConfig,
    ) -> HybridRetrievalResult:
        """Run the full hybrid retrieval pipeline."""
        started = time.perf_counter()
        diagnostics_stages: dict[str, RetrievalStageResult] = {}

        filter_config = FilterConfig(
            document_ids=query.filters.document_ids,
            document_types=query.filters.document_types,
            tags=query.filters.tags,
            date_from=query.filters.date_from.isoformat() if query.filters.date_from else None,
            date_to=query.filters.date_to.isoformat() if query.filters.date_to else None,
            min_trust_score=query.filters.min_trust_score,
            exclude_chunk_ids=query.filters.exclude_chunk_ids,
        )

        dense_candidates: list[RetrievalCandidate] = []
        dense_latency = 0
        if config.mode in {RetrievalMode.DENSE_ONLY, RetrievalMode.HYBRID}:
            dense_candidates, dense_latency = await self.dense_retriever.retrieve(
                query.text,
                top_k=config.dense_top_k,
                filter_config=filter_config,
            )
            diagnostics_stages["dense"] = self._stage_result("dense", dense_candidates, dense_latency)

        lexical_candidates: list[RetrievalCandidate] = []
        lexical_latency = 0
        if config.mode in {RetrievalMode.LEXICAL_ONLY, RetrievalMode.HYBRID}:
            lexical_candidates, lexical_latency = await self.lexical_retriever.retrieve(
                query.text,
                top_k=config.lexical_top_k,
                filter_config=filter_config,
            )
            diagnostics_stages["lexical"] = self._stage_result("lexical", lexical_candidates, lexical_latency)

        fusion_start = time.perf_counter()
        fused = self._fuse_candidates(dense_candidates, lexical_candidates, config)
        fusion_latency = int((time.perf_counter() - fusion_start) * 1000)
        diagnostics_stages["fused"] = self._stage_result("fused", fused, fusion_latency)

        filter_start = time.perf_counter()
        filtered = self.deduplicator.deduplicate(fused)
        if config.apply_metadata_filter:
            filtered = self.metadata_filter.apply(filtered, filter_config)
        if filter_config.min_trust_score is not None:
            filtered = self.trust_filter.apply(filtered, filter_config.min_trust_score)
        if config.apply_freshness_boost and filtered:
            filtered = self.freshness_booster.apply(filtered, self.metadata_store)
        filter_latency = int((time.perf_counter() - filter_start) * 1000)
        diagnostics_stages["filtered"] = self._stage_result("filtered", filtered, filter_latency)

        rerank_latency = 0
        final_candidates = filtered[: config.final_top_k]
        if config.rerank_enabled and filtered:
            reranked_candidates, rerank_latency = await self.reranking_service.rerank(
                query.text,
                filtered[: config.rerank_top_k],
                config.final_top_k,
            )
            final_candidates = reranked_candidates
            diagnostics_stages["reranked"] = self._stage_result("reranked", final_candidates, rerank_latency)

        if config.min_score_threshold is not None:
            final_candidates = [
                candidate
                for candidate in final_candidates
                if candidate.scores.final_score >= config.min_score_threshold
            ]
            for index, candidate in enumerate(final_candidates):
                candidate.rank = index

        total_latency = int((time.perf_counter() - started) * 1000)
        diagnostics = RetrievalDiagnostics(
            query_id=query.id,
            query_text=query.text,
            query_embedding_time_ms=self.dense_retriever.last_query_embedding_time_ms,
            dense_result=diagnostics_stages.get("dense"),
            lexical_result=diagnostics_stages.get("lexical"),
            fusion_result=diagnostics_stages.get("fused"),
            filter_result=diagnostics_stages.get("filtered"),
            rerank_result=diagnostics_stages.get("reranked"),
            final_candidates=[candidate.model_copy(deep=True) for candidate in final_candidates],
            total_latency_ms=total_latency,
            config=config,
        )
        self.diagnostics_store.put(diagnostics)
        return HybridRetrievalResult(
            query_id=query.id,
            candidates=final_candidates,
            total_candidates=len(final_candidates),
            diagnostics=diagnostics,
            dense_latency_ms=dense_latency,
            lexical_latency_ms=lexical_latency,
            fusion_latency_ms=fusion_latency,
            filter_latency_ms=filter_latency,
            rerank_latency_ms=rerank_latency,
            total_latency_ms=total_latency,
        )

    def _fuse_candidates(
        self,
        dense_candidates: list[RetrievalCandidate],
        lexical_candidates: list[RetrievalCandidate],
        config: RetrievalConfig,
    ) -> list[RetrievalCandidate]:
        if config.mode == RetrievalMode.DENSE_ONLY:
            return [candidate.model_copy(deep=True) for candidate in dense_candidates[: config.fusion_top_k]]
        if config.mode == RetrievalMode.LEXICAL_ONLY:
            return [candidate.model_copy(deep=True) for candidate in lexical_candidates[: config.fusion_top_k]]
        if config.fusion_method == FusionMethod.MAX_SCORE:
            return self._max_score_fusion(dense_candidates, lexical_candidates, config.fusion_top_k)
        strategy = self._get_fusion_strategy(config)
        return strategy.fuse(dense_candidates, lexical_candidates, config.fusion_top_k)

    def _get_fusion_strategy(self, config: RetrievalConfig) -> FusionStrategy:
        if config.fusion_method == FusionMethod.WEIGHTED:
            return WeightedScoreFusion(
                dense_weight=config.dense_weight,
                lexical_weight=config.lexical_weight,
            )
        return ReciprocalRankFusion(k=config.rrf_k)

    def _max_score_fusion(
        self,
        dense_candidates: list[RetrievalCandidate],
        lexical_candidates: list[RetrievalCandidate],
        top_k: int,
    ) -> list[RetrievalCandidate]:
        candidate_map: dict[str, RetrievalCandidate] = {}

        for candidate in dense_candidates + lexical_candidates:
            existing = candidate_map.get(candidate.chunk_id)
            if existing is None:
                candidate_map[candidate.chunk_id] = candidate.model_copy(deep=True)
                continue
            if candidate.scores.dense_score is not None:
                existing.scores.dense_score = candidate.scores.dense_score
            if candidate.scores.lexical_score is not None:
                existing.scores.lexical_score = candidate.scores.lexical_score
            existing.scores.final_score = max(existing.scores.final_score, candidate.scores.final_score)

        ranked = sorted(candidate_map.values(), key=lambda item: item.scores.final_score, reverse=True)[:top_k]
        for index, candidate in enumerate(ranked):
            candidate.source = RetrievalSource.HYBRID
            candidate.rank = index
        return ranked

    def _stage_result(
        self,
        stage: str,
        candidates: list[RetrievalCandidate],
        latency_ms: int,
    ) -> RetrievalStageResult:
        return RetrievalStageResult(
            stage=stage,
            candidates=[candidate.model_copy(deep=True) for candidate in candidates],
            count=len(candidates),
            latency_ms=latency_ms,
        )
