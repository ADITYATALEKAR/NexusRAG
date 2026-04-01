"""Decomposition service wrapper."""

from __future__ import annotations

from src.layer1_contracts.schemas.decomposition import DecompositionPlan
from src.layer1_contracts.schemas.query import Query, QueryType
from src.layer1_contracts.schemas.query_understanding import QueryAnalysis
from src.layer2_domain.decomposition.comparative import ComparativeDecomposer
from src.layer2_domain.decomposition.two_hop import TwoHopDecomposer


class DecompositionService:
    """Choose the bounded decomposition strategy for a routed query."""

    def __init__(
        self,
        comparative_decomposer: ComparativeDecomposer | None = None,
        two_hop_decomposer: TwoHopDecomposer | None = None,
    ) -> None:
        self.comparative_decomposer = comparative_decomposer or ComparativeDecomposer()
        self.two_hop_decomposer = two_hop_decomposer or TwoHopDecomposer()

    def create_plan(self, query: Query, analysis: QueryAnalysis) -> DecompositionPlan:
        """Return the appropriate decomposition plan for the query."""
        if analysis.query_type == QueryType.COMPARATIVE:
            return self.comparative_decomposer.decompose(query, analysis)
        return self.two_hop_decomposer.decompose(query, analysis)
