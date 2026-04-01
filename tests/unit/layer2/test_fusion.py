"""Tests for retrieval fusion strategies."""

from __future__ import annotations

from src.layer1_contracts.schemas.retrieval import RetrievalCandidate, RetrievalScores, RetrievalSource
from src.layer2_domain.retrieval.fusion.rrf import ReciprocalRankFusion
from src.layer2_domain.retrieval.fusion.weighted import WeightedScoreFusion


def make_candidate(
    chunk_id: str,
    rank: int,
    *,
    dense_score: float | None = None,
    lexical_score: float | None = None,
) -> RetrievalCandidate:
    return RetrievalCandidate(
        chunk_id=chunk_id,
        document_id=f"doc-{chunk_id}",
        content=f"content for {chunk_id}",
        scores=RetrievalScores(
            dense_score=dense_score,
            lexical_score=lexical_score,
            final_score=dense_score if dense_score is not None else lexical_score or 0.0,
        ),
        source=RetrievalSource.DENSE if dense_score is not None else RetrievalSource.LEXICAL,
        rank=rank,
    )


def test_rrf_fusion_merges_dense_and_lexical_rankings() -> None:
    """RRF should elevate items that appear in both ranked lists."""
    dense = [make_candidate("shared", 0, dense_score=0.9), make_candidate("dense-only", 1, dense_score=0.8)]
    lexical = [
        make_candidate("lex-only", 0, lexical_score=0.95),
        make_candidate("shared", 1, lexical_score=0.7),
    ]

    fused = ReciprocalRankFusion(k=60).fuse(dense, lexical, top_k=3)

    assert fused[0].chunk_id == "shared"
    assert fused[0].scores.dense_score == 0.9
    assert fused[0].scores.lexical_score == 0.7


def test_weighted_fusion_applies_configurable_weights() -> None:
    """Weighted fusion should prefer the modality with the larger configured weight."""
    dense = [make_candidate("dense-favored", 0, dense_score=0.9)]
    lexical = [make_candidate("lex-favored", 0, lexical_score=0.9)]

    fused = WeightedScoreFusion(dense_weight=0.8, lexical_weight=0.2).fuse(dense, lexical, top_k=2)

    assert fused[0].chunk_id == "dense-favored"
