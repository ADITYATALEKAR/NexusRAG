"""Sub-answer aggregation."""

from __future__ import annotations

from src.layer1_contracts.schemas.decomposition import AggregatedAnswer, SubQueryResult
from src.layer1_contracts.schemas.query import Query
from src.layer2_domain.generation.service import GenerationService


class SubAnswerAggregator:
    """Aggregate bounded sub-query results into a final answer."""

    def __init__(self, generation_service: GenerationService) -> None:
        self.generation_service = generation_service

    async def aggregate(
        self,
        original_query: Query,
        sub_results: list[SubQueryResult],
        strategy: str,
    ) -> AggregatedAnswer:
        """Aggregate sub-results using the configured strategy."""
        if strategy == "comparative":
            return await self._aggregate_comparative(original_query, sub_results)
        if strategy == "two_hop":
            return await self._aggregate_sequential(original_query, sub_results)
        return await self._aggregate_simple(original_query, sub_results)

    async def _aggregate_comparative(
        self,
        query: Query,
        sub_results: list[SubQueryResult],
    ) -> AggregatedAnswer:
        context = "\n\n".join(
            [f"Information {index + 1}:\n{sub_result.answer}" for index, sub_result in enumerate(sub_results)]
        )
        synthesis_query = Query(
            id=f"synth-{query.id}",
            text=f"Compare and contrast based on this information:\n\n{context}\n\nOriginal question: {query.text}",
        )
        final_answer = await self._synthesize(synthesis_query, context)
        return AggregatedAnswer(
            original_query_id=query.id,
            final_answer=final_answer,
            sub_results=sub_results,
            synthesis_strategy="comparative_synthesis",
            total_evidence=[evidence for result in sub_results for evidence in result.evidence_used],
        )

    async def _aggregate_sequential(
        self,
        query: Query,
        sub_results: list[SubQueryResult],
    ) -> AggregatedAnswer:
        final_answer = sub_results[-1].answer if sub_results else "Unable to answer"
        return AggregatedAnswer(
            original_query_id=query.id,
            final_answer=final_answer,
            sub_results=sub_results,
            synthesis_strategy="sequential",
            total_evidence=[evidence for result in sub_results for evidence in result.evidence_used],
        )

    async def _aggregate_simple(
        self,
        query: Query,
        sub_results: list[SubQueryResult],
    ) -> AggregatedAnswer:
        final_answer = sub_results[0].answer if sub_results else "Unable to answer"
        return AggregatedAnswer(
            original_query_id=query.id,
            final_answer=final_answer,
            sub_results=sub_results,
            synthesis_strategy="simple",
            total_evidence=[evidence for result in sub_results for evidence in result.evidence_used],
        )

    async def _synthesize(self, query: Query, context: str) -> str:
        del query
        return f"Based on the gathered information: {context[:500]}..."
