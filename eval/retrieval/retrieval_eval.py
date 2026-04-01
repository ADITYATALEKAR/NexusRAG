"""Helpers for running retrieval-focused evaluation."""

from __future__ import annotations

from src.layer1_contracts.schemas.evaluation import EvalDataset, EvalRunResult
from src.layer2_domain.evaluation.service import EvaluationService


async def run_retrieval_eval(service: EvaluationService, dataset: EvalDataset) -> EvalRunResult:
    """Run evaluation with the standard retrieval metrics pipeline."""
    return await service.evaluate_dataset(dataset, use_ragas=False)
