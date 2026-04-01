"""Answer flow state definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from src.layer1_contracts.schemas.answer import Answer
from src.layer1_contracts.schemas.evidence import EvidenceAssemblyResult, EvidenceConfig
from src.layer1_contracts.schemas.generation import GenerationConfig, GenerationTrace
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.retrieval import HybridRetrievalResult
from src.layer1_contracts.schemas.retrieval_config import RetrievalConfig


class AnswerFlowState(str, Enum):
    """Lifecycle states for answer generation."""

    INITIALIZED = "initialized"
    RETRIEVING = "retrieving"
    ASSEMBLING_EVIDENCE = "assembling_evidence"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AnswerFlowContext:
    """Mutable flow context shared across answer flow steps."""

    query: Query
    retrieval_config: RetrievalConfig
    evidence_config: EvidenceConfig
    generation_config: GenerationConfig
    state: AnswerFlowState = AnswerFlowState.INITIALIZED
    retrieval_result: HybridRetrievalResult | None = None
    evidence_result: EvidenceAssemblyResult | None = None
    answer: Answer | None = None
    trace: GenerationTrace | None = None
    errors: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
