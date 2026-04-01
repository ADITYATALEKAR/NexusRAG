"""Evaluation report generation helpers."""

from __future__ import annotations

import json

from src.layer1_contracts.schemas.evaluation import EvalRunResult, RegressionResult


def evaluation_report(result: EvalRunResult) -> str:
    """Render a compact JSON report for one evaluation run."""
    return json.dumps(result.model_dump(mode="json"), indent=2)


def regression_report(result: RegressionResult) -> str:
    """Render a compact JSON report for one regression run."""
    return json.dumps(result.model_dump(mode="json"), indent=2)
