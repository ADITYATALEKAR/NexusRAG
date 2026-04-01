"""Comparative decomposition."""

from __future__ import annotations

from src.layer1_contracts.schemas.decomposition import DecompositionPlan, SubQuery
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.query_understanding import QueryAnalysis


class ComparativeDecomposer:
    """Decompose comparative queries into bounded parallel sub-queries."""

    def decompose(self, query: Query, analysis: QueryAnalysis) -> DecompositionPlan:
        """Return a comparative plan from the routed analysis."""
        if analysis.sub_queries:
            sub_queries = [
                SubQuery(
                    id=f"{query.id}-sub-{index}",
                    text=sub_query,
                    purpose=self._infer_purpose(sub_query, index),
                    depends_on=[],
                    order=index,
                )
                for index, sub_query in enumerate(analysis.sub_queries)
            ]
        else:
            sub_queries = self._generate_default(query.text)

        return DecompositionPlan(
            original_query_id=query.id,
            original_text=query.text,
            sub_queries=sub_queries,
            strategy="comparative",
            max_hops=1,
        )

    def _infer_purpose(self, sub_query: str, index: int) -> str:
        if index < 2:
            return "Gather information about entity"
        return "Synthesize comparison"

    def _generate_default(self, text: str) -> list[SubQuery]:
        return [
            SubQuery(
                id="sub-0",
                text=f"Key aspects of the first item mentioned in: {text}",
                purpose="Understand first entity",
                depends_on=[],
                order=0,
            ),
            SubQuery(
                id="sub-1",
                text=f"Key aspects of the second item mentioned in: {text}",
                purpose="Understand second entity",
                depends_on=[],
                order=1,
            ),
        ]
