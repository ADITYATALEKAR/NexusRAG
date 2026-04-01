"""Golden dataset management."""

from __future__ import annotations

from pathlib import Path

from src.layer1_contracts.schemas.evaluation import EvalDataset


class GoldenDatasetManager:
    """Load and persist golden datasets for evaluation and regression."""

    def __init__(self, base_path: str = "eval/datasets") -> None:
        self.base_path = Path(base_path)

    def load(self, dataset_id: str) -> EvalDataset:
        """Load a dataset by identifier from the managed dataset roots."""
        path = self._resolve_dataset_path(dataset_id)
        return EvalDataset.model_validate_json(path.read_text(encoding="utf-8"))

    def save(self, dataset: EvalDataset, subset: str = "golden") -> Path:
        """Persist a dataset JSON file."""
        directory = self.base_path / subset
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{dataset.id}.json"
        path.write_text(dataset.model_dump_json(indent=2), encoding="utf-8")
        return path

    def list_datasets(self) -> list[str]:
        """Return all known dataset identifiers."""
        identifiers: list[str] = []
        for subset in ("golden", "regression"):
            directory = self.base_path / subset
            if not directory.exists():
                continue
            identifiers.extend(sorted(path.stem for path in directory.glob("*.json")))
        return identifiers

    def _resolve_dataset_path(self, dataset_id: str) -> Path:
        """Return the on-disk path for the requested dataset."""
        candidates = [
            self.base_path / "golden" / f"{dataset_id}.json",
            self.base_path / "regression" / f"{dataset_id}.json",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        raise FileNotFoundError(f"Dataset not found: {dataset_id}")
