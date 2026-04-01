"""Discrete ingestion flow steps."""

from __future__ import annotations

from src.layer3_flows.ingestion_flow.states import FlowContext


class ValidationStep:
    """Run file validation and initial document creation."""

    async def execute(self, flow: "IngestionFlow", context: FlowContext) -> None:
        """Execute the validation step."""
        await flow._validate(context)


class ParsingStep:
    """Run parsing and fallback selection."""

    async def execute(self, flow: "IngestionFlow", context: FlowContext) -> None:
        """Execute the parsing step."""
        await flow._parse(context)


class NormalizationStep:
    """Run normalization."""

    async def execute(self, flow: "IngestionFlow", context: FlowContext) -> None:
        """Execute the normalization step."""
        await flow._normalize(context)


class ChunkPreparationStep:
    """Prepare chunk precursors."""

    async def execute(self, flow: "IngestionFlow", context: FlowContext) -> None:
        """Execute chunk precursor preparation."""
        await flow._prepare_chunks(context)
