"""In-memory cost tracking."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from src.layer1_contracts.schemas.observability import CostRecord


class CostTracker:
    """Track per-request provider costs."""

    COSTS = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        "llama-3.1-70b-versatile": {"input": 0.59, "output": 0.79},
    }

    def __init__(self) -> None:
        self._records: list[CostRecord] = []

    def record(
        self,
        request_id: str,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> CostRecord:
        """Record one provider call cost."""
        rates = self.COSTS.get(model, {"input": 1.0, "output": 1.0})
        cost = (prompt_tokens * rates["input"] + completion_tokens * rates["output"]) / 1_000_000.0
        record = CostRecord(
            request_id=request_id,
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost,
            timestamp=datetime.now(timezone.utc),
        )
        self._records.append(record)
        return record

    def get_total_cost(self, since: datetime | None = None) -> float:
        """Return total cost optionally filtered by timestamp."""
        records = self._records if since is None else [record for record in self._records if record.timestamp >= since]
        return sum(record.cost_usd for record in records)

    def get_cost_by_model(self, since: datetime | None = None) -> dict[str, float]:
        """Return cost grouped by model."""
        records = self._records if since is None else [record for record in self._records if record.timestamp >= since]
        totals: defaultdict[str, float] = defaultdict(float)
        for record in records:
            totals[record.model] += record.cost_usd
        return dict(totals)

    def get_records(self, since: datetime | None = None) -> list[CostRecord]:
        """Return recorded costs optionally filtered by timestamp."""
        if since is None:
            return list(self._records)
        return [record for record in self._records if record.timestamp >= since]

    def clear(self) -> None:
        """Clear tracked records for tests."""
        self._records.clear()


cost_tracker = CostTracker()
