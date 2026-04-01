"""Retrieval flow state definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.retrieval import HybridRetrievalResult
from src.layer1_contracts.schemas.retrieval_config import RetrievalConfig


class RetrievalFlowState(str, Enum):
    """Lifecycle states for retrieval orchestration."""

    INITIALIZED = "initialized"
    RETRIEVING = "retrieving"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class RetrievalFlowContext:
    """Mutable context passed through retrieval flow steps."""

    query: Query
    config: RetrievalConfig
    state: RetrievalFlowState = RetrievalFlowState.INITIALIZED
    result: HybridRetrievalResult | None = None
    errors: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
