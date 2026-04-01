"""Retrieval flow orchestrator."""

from __future__ import annotations

from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.retrieval import HybridRetrievalResult
from src.layer1_contracts.schemas.retrieval_config import RetrievalConfig
from src.layer2_domain.retrieval.service import RetrievalService
from src.layer3_flows.retrieval_flow.states import RetrievalFlowContext, RetrievalFlowState
from src.layer3_flows.retrieval_flow.steps import RetrievalStep


class RetrievalFlow:
    """Thin flow wrapper around the Phase 3 retrieval service."""

    def __init__(self, retrieval_service: RetrievalService) -> None:
        self.retrieval_service = retrieval_service
        self.retrieval_step = RetrievalStep()

    async def execute(
        self,
        query: Query,
        config: RetrievalConfig | None = None,
    ) -> HybridRetrievalResult:
        """Execute the retrieval flow."""
        context = RetrievalFlowContext(query=query, config=config or self.retrieval_service.default_config)
        try:
            context.state = RetrievalFlowState.RETRIEVING
            await self.retrieval_step.execute(self, context)
            context.state = RetrievalFlowState.COMPLETED
            if context.result is None:
                raise ValueError("Retrieval flow completed without a result")
            return context.result
        except Exception as error:  # noqa: BLE001
            context.state = RetrievalFlowState.FAILED
            context.errors.append(str(error))
            raise

    async def _retrieve(self, context: RetrievalFlowContext) -> None:
        """Run retrieval via the underlying service."""
        context.result = await self.retrieval_service.retrieve(context.query, context.config)
