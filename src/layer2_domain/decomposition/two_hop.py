"""Two-hop decomposition."""

from __future__ import annotations

import re

from src.layer1_contracts.schemas.decomposition import DecompositionPlan, SubQuery
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.query_understanding import QueryAnalysis


class TwoHopDecomposer:
    """Decompose queries that require at most two retrieval hops."""

    def decompose(self, query: Query, analysis: QueryAnalysis) -> DecompositionPlan:
        """Return a two-hop plan for the given query."""
        intermediate = self._detect_intermediate(query.text, analysis)
        sub_queries = [
            SubQuery(
                id=f"{query.id}-hop1",
                text=intermediate["first_query"],
                purpose="Find intermediate information",
                depends_on=[],
                order=0,
            ),
            SubQuery(
                id=f"{query.id}-hop2",
                text=intermediate["second_query"],
                purpose="Answer using intermediate result",
                depends_on=[f"{query.id}-hop1"],
                order=1,
            ),
        ]
        return DecompositionPlan(
            original_query_id=query.id,
            original_text=query.text,
            sub_queries=sub_queries,
            strategy="two_hop",
            max_hops=2,
        )

    def _detect_intermediate(self, text: str, analysis: QueryAnalysis) -> dict[str, str]:
        del analysis
        patterns = [
            (r"(.+)\s+that\s+(.+)", "that"),
            (r"(.+)\s+which\s+(.+)", "which"),
            (r"(.+)\s+who\s+(.+)", "who"),
        ]
        for pattern, _ in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    "first_query": match.group(2).strip() + "?",
                    "second_query": match.group(1).strip() + " [RESULT]?",
                }
        return {"first_query": text, "second_query": text}
