"""Steps for the structured query flow."""

from __future__ import annotations

from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.structured import StructuredQuery, StructuredResult


class InferStructuredQueryStep:
    """Infer a structured query from natural language."""

    async def execute(self, flow: "StructuredQueryFlow", query: Query) -> StructuredQuery:
        """Return the structured query produced by the flow's service."""
        return flow.structured_service.build_query(query.id, query.text)


class ExecuteStructuredQueryStep:
    """Execute the structured query and return its result."""

    async def execute(
        self,
        flow: "StructuredQueryFlow",
        structured_query: StructuredQuery,
    ) -> StructuredResult:
        """Run the structured query against the configured service."""
        return await flow.structured_service.execute(structured_query)
