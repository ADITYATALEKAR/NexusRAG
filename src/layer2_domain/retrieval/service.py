"""Main retrieval service entry point."""

from __future__ import annotations

from typing import Protocol

from src.layer0_core.ids.base import QueryId
from src.layer1_contracts.schemas.query import Query, QueryConfig
from src.layer1_contracts.schemas.retrieval import HybridRetrievalResult, RetrievalCandidate, RetrievalDiagnostics
from src.layer1_contracts.schemas.retrieval_config import RetrievalConfig, RetrievalMode


class RetrievalOrchestratorProtocol(Protocol):
    """Protocol for retrieval orchestrators used by the public service facade."""

    diagnostics_store: object | None

    async def retrieve(self, query: Query, config: RetrievalConfig) -> HybridRetrievalResult: ...


class RetrievalService:
    """Public service interface for retrieval operations."""

    def __init__(
        self,
        orchestrator: RetrievalOrchestratorProtocol,
        default_config: RetrievalConfig | None = None,
    ) -> None:
        self.orchestrator = orchestrator
        self.default_config = default_config or RetrievalConfig()

    async def retrieve(
        self,
        query: Query,
        config: RetrievalConfig | None = None,
    ) -> HybridRetrievalResult:
        """Run a retrieval query using the configured orchestrator."""
        retrieval_config = config or self.default_config
        return await self.orchestrator.retrieve(query, retrieval_config)

    async def retrieve_simple(
        self,
        query_text: str,
        top_k: int = 10,
        mode: RetrievalMode = RetrievalMode.HYBRID,
    ) -> list[RetrievalCandidate]:
        """Simplified retrieval helper for tests and diagnostics."""
        query = Query(
            id=QueryId.generate().value,
            text=query_text,
            config=QueryConfig(top_k=top_k, rerank_top_k=max(top_k, self.default_config.rerank_top_k)),
        )
        result = await self.retrieve(
            query,
            RetrievalConfig(
                mode=mode,
                final_top_k=top_k,
                rerank_top_k=max(top_k, self.default_config.rerank_top_k),
            ),
        )
        return result.candidates

    def get_diagnostics(self, query_id: str) -> RetrievalDiagnostics | None:
        """Return cached diagnostics for a previous query if available."""
        diagnostics_store = getattr(self.orchestrator, "diagnostics_store", None)
        if diagnostics_store is None:
            return None
        return diagnostics_store.get(query_id)
