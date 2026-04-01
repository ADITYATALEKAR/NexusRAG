"""Flow state definitions for indexing."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from src.layer1_contracts.schemas.chunking import ChunkingConfig, ChunkingResult
from src.layer1_contracts.schemas.indexing import IndexingResult
from src.layer1_contracts.schemas.normalization import ChunkPrecursor, NormalizedDocument


class IndexingFlowState(str, Enum):
    """Indexing flow states."""

    INITIALIZED = "initialized"
    CHECKING_FRESHNESS = "checking_freshness"
    CHUNKING = "chunking"
    INDEXING = "indexing"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass
class IndexingFlowContext:
    """Mutable context for the indexing flow."""

    normalized_doc: NormalizedDocument
    chunk_precursors: list[ChunkPrecursor]
    document_checksum: str
    config: ChunkingConfig | None = None
    state: IndexingFlowState = IndexingFlowState.INITIALIZED
    chunking_result: ChunkingResult | None = None
    indexing_result: IndexingResult | None = None
    errors: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
