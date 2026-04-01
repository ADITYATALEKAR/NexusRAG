"""Chunking contracts."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from src.layer1_contracts.schemas.chunk import Chunk
from src.layer1_contracts.schemas.normalization import ChunkPrecursor


class ChunkingStrategy(str, Enum):
    """Supported chunking strategies."""

    FIXED_SIZE = "fixed_size"
    SEMANTIC = "semantic"
    HIERARCHICAL = "hierarchical"


class ChunkingConfig(BaseModel):
    """Configuration for chunk generation."""

    model_config = ConfigDict(extra="forbid")

    strategy: ChunkingStrategy = ChunkingStrategy.SEMANTIC
    target_size: int = Field(default=512, ge=64, le=2048)
    min_size: int = Field(default=64, ge=32)
    max_size: int = Field(default=1024, le=4096)
    overlap: int = Field(default=64, ge=0, le=256)
    preserve_sentences: bool = True
    preserve_paragraphs: bool = True


class ChunkingRequest(BaseModel):
    """Request to chunk normalized content."""

    model_config = ConfigDict(extra="forbid")

    id: str
    document_id: str
    normalized_content: str
    chunk_precursors: list[ChunkPrecursor]
    config: ChunkingConfig = Field(default_factory=ChunkingConfig)


class ChunkingResult(BaseModel):
    """Result of a chunking operation."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    document_id: str
    chunks: list[Chunk]
    total_chunks: int
    avg_chunk_size: float
    strategy_used: ChunkingStrategy
    processing_time_ms: int
