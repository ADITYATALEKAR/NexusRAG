"""Structured query flow orchestration."""

from __future__ import annotations

from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.structured import StructuredQuery, StructuredResult
from src.layer2_domain.structured_retrieval.service import StructuredRetrievalService
from src.layer3_flows.structured_query_flow.steps import (
    ExecuteStructuredQueryStep,
    InferStructuredQueryStep,
)


class StructuredQueryFlow:
    """Convert a natural-language query into bounded structured retrieval."""

    def __init__(self, structured_service: StructuredRetrievalService) -> None:
        self.structured_service = structured_service
        self.infer_step = InferStructuredQueryStep()
        self.execute_step = ExecuteStructuredQueryStep()

    async def execute(
        self,
        query: Query,
        structured_query: StructuredQuery | None = None,
    ) -> StructuredResult:
        """Infer and execute a structured query."""
        planned_query = structured_query or await self.infer_step.execute(self, query)
        return await self.execute_step.execute(self, planned_query)
