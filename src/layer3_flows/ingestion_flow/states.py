"""Flow state definitions for ingestion."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from src.layer1_contracts.schemas.document import Document
from src.layer1_contracts.schemas.ingestion import IngestionRequest
from src.layer1_contracts.schemas.normalization import ChunkPrecursor, NormalizedDocument
from src.layer1_contracts.schemas.parsing import ParseResult


class FlowState(str, Enum):
    """Ingestion flow states."""

    INITIALIZED = "initialized"
    VALIDATING = "validating"
    PARSING = "parsing"
    NORMALIZING = "normalizing"
    PREPARING = "preparing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class FlowContext:
    """Mutable context passed through the ingestion flow."""

    request: IngestionRequest
    state: FlowState = FlowState.INITIALIZED
    document: Document | None = None
    parse_result: ParseResult | None = None
    normalized_doc: NormalizedDocument | None = None
    chunk_precursors: list[ChunkPrecursor] | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
