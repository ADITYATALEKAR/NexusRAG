"""Bounded multi-hop orchestration."""

from __future__ import annotations

from src.layer1_contracts.schemas.decomposition import AggregatedAnswer
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.query_understanding import QueryAnalysis
from src.layer2_domain.decomposition.aggregator import SubAnswerAggregator
from src.layer2_domain.decomposition.two_hop import TwoHopDecomposer
from src.layer3_flows.answer_flow.flow import AnswerFlow
from src.layer3_flows.multi_hop_flow.steps import (
    AggregateSubAnswersStep,
    ExecuteSubQueriesStep,
    PlanMultiHopStep,
)


class MultiHopFlow:
    """Execute a bounded two-hop retrieval plan."""

    def __init__(
        self,
        standard_flow: AnswerFlow,
        two_hop_decomposer: TwoHopDecomposer,
        aggregator: SubAnswerAggregator,
    ) -> None:
        self.standard_flow = standard_flow
        self.two_hop_decomposer = two_hop_decomposer
        self.aggregator = aggregator
        self.plan_step = PlanMultiHopStep()
        self.execute_sub_queries_step = ExecuteSubQueriesStep()
        self.aggregate_step = AggregateSubAnswersStep()

    async def execute(self, query: Query, analysis: QueryAnalysis) -> AggregatedAnswer:
        """Execute a bounded two-hop query plan."""
        plan = self.plan_step.execute(self, query, analysis)
        sub_results = await self.execute_sub_queries_step.execute(self, plan)
        return await self.aggregate_step.execute(self, query, sub_results)
