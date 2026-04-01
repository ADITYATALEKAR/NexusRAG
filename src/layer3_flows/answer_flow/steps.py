"""Discrete answer flow steps."""

from __future__ import annotations

from src.layer3_flows.answer_flow.states import AnswerFlowContext


class RetrieveStep:
    """Execute retrieval for the answer flow."""

    async def execute(self, flow: "AnswerFlow", context: AnswerFlowContext) -> None:
        """Run retrieval using the underlying retrieval service."""
        await flow._retrieve(context)


class AssembleEvidenceStep:
    """Execute evidence assembly for the answer flow."""

    async def execute(self, flow: "AnswerFlow", context: AnswerFlowContext) -> None:
        """Run evidence assembly from retrieval candidates."""
        await flow._assemble_evidence(context)


class GenerateAnswerStep:
    """Execute answer generation for the answer flow."""

    async def execute(self, flow: "AnswerFlow", context: AnswerFlowContext) -> None:
        """Generate the final answer and trace."""
        await flow._generate_answer(context)
