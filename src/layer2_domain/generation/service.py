"""Answer generation service."""

from __future__ import annotations

from src.layer1_contracts.schemas.answer import Answer, AnswerMetadata, AnswerStatus
from src.layer1_contracts.schemas.generation import AbstentionReason, GenerationRequest
from src.layer1_contracts.schemas.llm import LLMConfig, LLMRequest, LLMResponse
from src.layer2_domain.citations.extractor import CitationExtractor
from src.layer2_domain.citations.validator import CitationValidator
from src.layer2_domain.failover.service import FailoverService
from src.layer2_domain.generation.abstention import AbstentionChecker
from src.layer2_domain.generation.answer_parser import AnswerParser
from src.layer2_domain.generation.grounding import GroundingValidator
from src.layer2_domain.generation.prompt_builder import PromptBuilder


class GenerationService:
    """Generate grounded answers from evidence bundles."""

    def __init__(
        self,
        failover_service: FailoverService,
        prompt_builder: PromptBuilder,
        citation_extractor: CitationExtractor,
        citation_validator: CitationValidator,
        abstention_checker: AbstentionChecker,
        grounding_validator: GroundingValidator,
        answer_parser: AnswerParser | None = None,
        default_model: str = "gpt-4o",
    ) -> None:
        self.failover_service = failover_service
        self.prompt_builder = prompt_builder
        self.citation_extractor = citation_extractor
        self.citation_validator = citation_validator
        self.abstention_checker = abstention_checker
        self.grounding_validator = grounding_validator
        self.answer_parser = answer_parser or AnswerParser(citation_extractor, citation_validator)
        self.default_model = default_model

    async def generate(self, request: GenerationRequest) -> Answer:
        """Generate an answer or abstention from evidence."""
        should_abstain, reason = self.abstention_checker.should_abstain_before_generation(
            request.evidence_bundle
        )
        if should_abstain:
            return self._create_abstention_answer(request, reason)

        messages = self.prompt_builder.build(
            request.query,
            request.evidence_bundle,
            request.config,
            request.system_prompt_override,
        )
        llm_request = LLMRequest(
            id=f"llm-{request.id}",
            messages=messages,
            config=LLMConfig(
                model=request.config.model or self.default_model,
                temperature=request.config.temperature,
                max_tokens=request.config.max_output_tokens,
            ),
            timeout_seconds=60.0,
        )

        llm_response = await self.failover_service.execute(llm_request)
        abstained, abstention_reason = self.abstention_checker.detect_abstention_in_response(
            llm_response.content
        )
        if abstained:
            return self._create_abstention_answer(
                request,
                abstention_reason,
                generated_text=llm_response.content,
                llm_response=llm_response,
            )

        citations, is_valid, issues = self.answer_parser.parse(
            llm_response.content,
            request.evidence_bundle,
        )
        is_grounded, _, grounding_issues = self.grounding_validator.validate(
            llm_response.content,
            citations,
            request.evidence_bundle,
            request.config.grounding_threshold,
        )
        final_issues = issues + grounding_issues
        status = AnswerStatus.SUCCESS
        if request.config.require_citations and (not is_valid or not is_grounded):
            status = AnswerStatus.PARTIAL

        return Answer(
            id=f"ans-{request.id}",
            query_id=request.query.id,
            text=llm_response.content,
            status=status,
            citations=citations,
            evidence_bundle_id=request.evidence_bundle.query_id,
            evidence_item_ids=[item.chunk_id for item in request.evidence_bundle.items],
            metadata=AnswerMetadata(
                model_used=llm_response.model,
                provider_used=llm_response.provider,
                fallback_occurred=llm_response.failover_occurred,
                fallback_chain=llm_response.providers_attempted,
                prompt_tokens=llm_response.usage.prompt_tokens,
                completion_tokens=llm_response.usage.completion_tokens,
                generation_latency_ms=llm_response.latency_ms,
            ),
            abstention_reason='; '.join(final_issues) if status == AnswerStatus.PARTIAL and final_issues else None,
        )

    def _create_abstention_answer(
        self,
        request: GenerationRequest,
        reason: AbstentionReason | None,
        generated_text: str | None = None,
        llm_response: LLMResponse | None = None,
    ) -> Answer:
        """Create a typed abstention answer."""
        text = generated_text or (
            f"I cannot answer this question based on the available evidence because {reason.value}."
            if reason is not None
            else "I cannot answer this question based on the available evidence."
        )
        return Answer(
            id=f"ans-{request.id}",
            query_id=request.query.id,
            text=text,
            status=AnswerStatus.ABSTAINED,
            citations=[],
            evidence_bundle_id=request.evidence_bundle.query_id,
            evidence_item_ids=[item.chunk_id for item in request.evidence_bundle.items],
            metadata=AnswerMetadata(
                model_used=llm_response.model if llm_response else "none",
                provider_used=llm_response.provider if llm_response else "none",
                fallback_occurred=llm_response.failover_occurred if llm_response else False,
                fallback_chain=llm_response.providers_attempted if llm_response else [],
                prompt_tokens=llm_response.usage.prompt_tokens if llm_response else 0,
                completion_tokens=llm_response.usage.completion_tokens if llm_response else 0,
                generation_latency_ms=llm_response.latency_ms if llm_response else 0,
            ),
            abstention_reason=reason.value if reason is not None else None,
        )
