"""Discrete indexing flow steps."""

from __future__ import annotations

from src.layer3_flows.indexing_flow.states import IndexingFlowContext


class FreshnessStep:
    """Check whether indexing work is needed."""

    async def execute(self, flow: "IndexingFlow", context: IndexingFlowContext) -> None:
        """Execute freshness evaluation."""
        await flow._check_freshness(context)


class ChunkingStep:
    """Generate retrieval-ready chunks."""

    async def execute(self, flow: "IndexingFlow", context: IndexingFlowContext) -> None:
        """Execute chunking."""
        await flow._chunk(context)


class IndexingStep:
    """Index generated chunks into storage backends."""

    async def execute(self, flow: "IndexingFlow", context: IndexingFlowContext) -> None:
        """Execute storage indexing."""
        await flow._index(context)
