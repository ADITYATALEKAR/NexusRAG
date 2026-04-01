"""Discrete retrieval flow steps."""

from __future__ import annotations

from src.layer3_flows.retrieval_flow.states import RetrievalFlowContext


class RetrievalStep:
    """Execute the retrieval stage."""

    async def execute(self, flow: "RetrievalFlow", context: RetrievalFlowContext) -> None:
        """Run the retrieval step."""
        await flow._retrieve(context)
