"""Answer flow orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone

from src.layer1_contracts.schemas.answer import Answer
from src.layer1_contracts.schemas.evidence import EvidenceConfig
from src.layer1_contracts.schemas.generation import GenerationConfig, GenerationRequest, GenerationTrace
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.retrieval_config import RetrievalConfig
from src.layer2_domain.evidence.service import EvidenceService
from src.layer2_domain.generation.service import GenerationService
from src.layer2_domain.retrieval.service import RetrievalService
from src.layer3_flows.answer_flow.states import AnswerFlowContext, AnswerFlowState
from src.layer3_flows.answer_flow.steps import AssembleEvidenceStep, GenerateAnswerStep, RetrieveStep


class AnswerFlow:
    """Full answer generation flow: retrieval to evidence to grounded answer."""

    def __init__(
        self,
        retrieval_service: RetrievalService,
        evidence_service: EvidenceService,
        generation_service: GenerationService,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.evidence_service = evidence_service
        self.generation_service = generation_service
        self.retrieve_step = RetrieveStep()
        self.assemble_evidence_step = AssembleEvidenceStep()
        self.generate_answer_step = GenerateAnswerStep()

    async def execute(
        self,
        query: Query,
        retrieval_config: RetrievalConfig | None = None,
        evidence_config: EvidenceConfig | None = None,
        generation_config: GenerationConfig | None = None,
    ) -> tuple[Answer, GenerationTrace]:
        """Execute the full answer generation pipeline."""
        context = AnswerFlowContext(
            query=query,
            retrieval_config=retrieval_config or self.retrieval_service.default_config,
            evidence_config=evidence_config or EvidenceConfig(),
            generation_config=generation_config or GenerationConfig(),
        )
        try:
            context.state = AnswerFlowState.RETRIEVING
            await self.retrieve_step.execute(self, context)
            context.state = AnswerFlowState.ASSEMBLING_EVIDENCE
            await self.assemble_evidence_step.execute(self, context)
            context.state = AnswerFlowState.GENERATING
            await self.generate_answer_step.execute(self, context)
            context.state = AnswerFlowState.COMPLETED
            if context.answer is None or context.trace is None:
                raise ValueError("Answer flow completed without answer or trace")
            return context.answer, context.trace
        except Exception as error:  # noqa: BLE001
            context.state = AnswerFlowState.FAILED
            context.errors.append(str(error))
            raise

    async def _retrieve(self, context: AnswerFlowContext) -> None:
        """Retrieve candidates for the answer query."""
        context.retrieval_result = await self.retrieval_service.retrieve(
            context.query,
            context.retrieval_config,
        )

    async def _assemble_evidence(self, context: AnswerFlowContext) -> None:
        """Assemble an evidence bundle from retrieval candidates."""
        if context.retrieval_result is None:
            raise ValueError("Retrieval must complete before evidence assembly")
        context.evidence_result = await self.evidence_service.assemble(
            context.retrieval_result.candidates,
            context.query,
            context.evidence_config,
        )

    async def _generate_answer(self, context: AnswerFlowContext) -> None:
        """Generate the answer and build its trace."""
        if context.evidence_result is None:
            raise ValueError("Evidence assembly must complete before generation")
        generation_request = GenerationRequest(
            id=f"gen-{context.query.id}",
            query=context.query,
            evidence_bundle=context.evidence_result.bundle,
            config=context.generation_config,
            request_id=context.query.request_id,
        )
        context.answer = await self.generation_service.generate(generation_request)
        latency_ms = int((datetime.now(timezone.utc) - context.started_at).total_seconds() * 1000)
        context.trace = GenerationTrace(
            request_id=context.query.id,
            query_text=context.query.text,
            evidence_items=[item.chunk_id for item in context.evidence_result.bundle.items],
            prompt_tokens=context.answer.metadata.prompt_tokens or 0,
            completion_tokens=context.answer.metadata.completion_tokens or 0,
            provider_used=context.answer.metadata.provider_used,
            model_used=context.answer.metadata.model_used,
            fallback_occurred=context.answer.metadata.fallback_occurred,
            fallback_chain=context.answer.metadata.fallback_chain,
            latency_ms=latency_ms,
        )
