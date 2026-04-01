"""Regression testing for evaluation runs."""

from __future__ import annotations

from pathlib import Path

from src.layer1_contracts.schemas.evaluation import EvalDataset, EvalRunResult, RegressionResult
from src.layer2_domain.evaluation.service import EvaluationService


class RegressionTestRunner:
    """Compare current evaluation runs against stored baselines."""

    def __init__(
        self,
        eval_service: EvaluationService,
        baseline_path: str = "eval/datasets/regression",
        regression_tolerance: float = 0.05,
        latency_tolerance: float = 0.20,
    ) -> None:
        self.eval_service = eval_service
        self.baseline_path = Path(baseline_path)
        self.regression_tolerance = regression_tolerance
        self.latency_tolerance = latency_tolerance

    async def run(self, dataset: EvalDataset, baseline_id: str) -> RegressionResult:
        """Evaluate the current system and compare it to the requested baseline."""
        current = await self.eval_service.evaluate_dataset(dataset)
        baseline = self._load_baseline(baseline_id)
        regressions: list[str] = []
        improvements: list[str] = []

        for k in [5, 10]:
            current_recall = current.retrieval_metrics.recall_at_k.get(k, 0.0)
            baseline_recall = baseline.retrieval_metrics.recall_at_k.get(k, 0.0)
            if current_recall < baseline_recall * (1.0 - self.regression_tolerance):
                regressions.append(f"recall@{k}: {baseline_recall:.3f} -> {current_recall:.3f}")
            elif current_recall > baseline_recall * (1.0 + self.regression_tolerance):
                improvements.append(f"recall@{k}: {baseline_recall:.3f} -> {current_recall:.3f}")

        current_faithfulness = current.generation_metrics.faithfulness
        baseline_faithfulness = baseline.generation_metrics.faithfulness
        if current_faithfulness < baseline_faithfulness * (1.0 - self.regression_tolerance):
            regressions.append(
                f"faithfulness: {baseline_faithfulness:.3f} -> {current_faithfulness:.3f}"
            )
        elif current_faithfulness > baseline_faithfulness * (1.0 + self.regression_tolerance):
            improvements.append(
                f"faithfulness: {baseline_faithfulness:.3f} -> {current_faithfulness:.3f}"
            )

        if current.p95_latency_ms > baseline.p95_latency_ms * (1.0 + self.latency_tolerance):
            regressions.append(
                f"p95_latency: {baseline.p95_latency_ms:.0f}ms -> {current.p95_latency_ms:.0f}ms"
            )
        elif current.p95_latency_ms < baseline.p95_latency_ms * (1.0 - self.latency_tolerance):
            improvements.append(
                f"p95_latency: {baseline.p95_latency_ms:.0f}ms -> {current.p95_latency_ms:.0f}ms"
            )

        return RegressionResult(
            current=current,
            baseline=baseline,
            regressions=regressions,
            improvements=improvements,
            passed=len(regressions) == 0,
        )

    def save_baseline(self, result: EvalRunResult, baseline_id: str) -> Path:
        """Persist an evaluation result as a regression baseline."""
        path = self.baseline_path / f"{baseline_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        return path

    def _load_baseline(self, baseline_id: str) -> EvalRunResult:
        """Load the named regression baseline."""
        path = self.baseline_path / f"{baseline_id}.json"
        return EvalRunResult.model_validate_json(path.read_text(encoding="utf-8"))
