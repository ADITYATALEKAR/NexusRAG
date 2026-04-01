"""Helpers for running generation-focused evaluation."""

from __future__ import annotations

from src.layer1_contracts.schemas.evaluation import EvalDataset, EvalRunResult
from src.layer2_domain.evaluation.service import EvaluationService


async def run_generation_eval(service: EvaluationService, dataset: EvalDataset) -> EvalRunResult:
    """Run evaluation with generation metrics emphasized."""
    return await service.evaluate_dataset(dataset, use_ragas=False)
