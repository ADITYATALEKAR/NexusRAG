"""Chunking service."""

from __future__ import annotations

from datetime import datetime, timezone

from src.layer1_contracts.schemas.chunk import Chunk
from src.layer1_contracts.schemas.chunking import (
    ChunkingConfig,
    ChunkingRequest,
    ChunkingResult,
    ChunkingStrategy,
)
from src.layer2_domain.chunking.metadata_enricher import ChunkMetadataEnricher
from src.layer2_domain.chunking.overlap import OverlapHandler
from src.layer2_domain.chunking.strategies.base import ChunkingStrategyBase
from src.layer2_domain.chunking.strategies.fixed_size import FixedSizeStrategy
from src.layer2_domain.chunking.strategies.hierarchical import HierarchicalStrategy
from src.layer2_domain.chunking.strategies.semantic import SemanticBoundaryStrategy


class ChunkingService:
    """Convert normalized content and chunk precursors into retrieval-ready chunks."""

    STRATEGIES: dict[ChunkingStrategy, type[ChunkingStrategyBase]] = {
        ChunkingStrategy.FIXED_SIZE: FixedSizeStrategy,
        ChunkingStrategy.SEMANTIC: SemanticBoundaryStrategy,
        ChunkingStrategy.HIERARCHICAL: HierarchicalStrategy,
    }

    def __init__(
        self,
        default_config: ChunkingConfig | None = None,
        overlap_handler: OverlapHandler | None = None,
        metadata_enricher: ChunkMetadataEnricher | None = None,
    ) -> None:
        self.default_config = default_config or ChunkingConfig()
        self.overlap_handler = overlap_handler or OverlapHandler()
        self.metadata_enricher = metadata_enricher or ChunkMetadataEnricher()

    async def chunk(self, request: ChunkingRequest) -> ChunkingResult:
        """Chunk normalized content according to the chosen strategy."""
        start = datetime.now(timezone.utc)
        config = request.config or self.default_config

        strategy_class = self.STRATEGIES[config.strategy]
        strategy = strategy_class(config=config, metadata_enricher=self.metadata_enricher)
        chunks = strategy.chunk(request.normalized_content, request.chunk_precursors)
        for chunk in chunks:
            chunk.document_id = request.document_id

        if config.overlap > 0 and config.strategy != ChunkingStrategy.HIERARCHICAL:
            chunks = self.overlap_handler.apply(chunks, config.overlap)

        elapsed_ms = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
        avg_size = sum(len(chunk.content) for chunk in chunks) / len(chunks) if chunks else 0.0
        return ChunkingResult(
            request_id=request.id,
            document_id=request.document_id,
            chunks=chunks,
            total_chunks=len(chunks),
            avg_chunk_size=avg_size,
            strategy_used=config.strategy,
            processing_time_ms=elapsed_ms,
        )
