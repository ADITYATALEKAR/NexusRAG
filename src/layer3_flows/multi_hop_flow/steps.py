"""Steps for the bounded multi-hop flow."""

from __future__ import annotations

from src.layer1_contracts.schemas.decomposition import DecompositionPlan, SubQueryResult
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.query_understanding import QueryAnalysis


class PlanMultiHopStep:
    """Create a bounded multi-hop plan."""

    def execute(self, flow: "MultiHopFlow", query: Query, analysis: QueryAnalysis) -> DecompositionPlan:
        """Return a two-hop plan from the decomposer."""
        return flow.two_hop_decomposer.decompose(query, analysis)


class ExecuteSubQueriesStep:
    """Run sub-queries in order, carrying forward intermediate answers."""

    async def execute(
        self,
        flow: "MultiHopFlow",
        plan: DecompositionPlan,
    ) -> list[SubQueryResult]:
        """Execute each hop and collect its answer and evidence."""
        sub_results: list[SubQueryResult] = []
        previous_answer = ""
        for sub_query in sorted(plan.sub_queries, key=lambda item: item.order):
            query_text = sub_query.text.replace("[RESULT]", previous_answer)
            sub_query_input = Query(id=sub_query.id, text=query_text)
            answer, _ = await flow.standard_flow.execute(sub_query_input)
            sub_results.append(
                SubQueryResult(
                    sub_query_id=sub_query.id,
                    answer=answer.text,
                    evidence_used=[citation.chunk_id for citation in answer.citations],
                    confidence=0.8,
                )
            )
            previous_answer = answer.text
        return sub_results


class AggregateSubAnswersStep:
    """Aggregate executed sub-query answers."""

    async def execute(
        self,
        flow: "MultiHopFlow",
        query: Query,
        sub_results: list[SubQueryResult],
    ):
        """Aggregate multi-hop sub-results into a final answer."""
        return await flow.aggregator.aggregate(query, sub_results, "two_hop")
