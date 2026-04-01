"""Helpers for running RAGAS-style evaluation."""

from __future__ import annotations

from src.layer1_contracts.schemas.evaluation import EvalDataset, EvalRunResult
from src.layer2_domain.evaluation.service import EvaluationService


async def run_ragas_eval(service: EvaluationService, dataset: EvalDataset) -> EvalRunResult:
    """Run evaluation with RAGAS-style adapter calls enabled."""
    return await service.evaluate_dataset(dataset, use_ragas=True)
