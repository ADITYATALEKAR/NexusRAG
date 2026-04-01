"""Indexing flow."""

from __future__ import annotations

from src.layer1_contracts.schemas.chunking import ChunkingConfig, ChunkingRequest
from src.layer1_contracts.schemas.document import Document, DocumentType
from src.layer1_contracts.schemas.indexing import IndexStatus, IndexingResult
from src.layer1_contracts.schemas.normalization import ChunkPrecursor, NormalizedDocument
from src.layer2_domain.chunking.service import ChunkingService
from src.layer2_domain.indexing.freshness import FreshnessTracker
from src.layer2_domain.indexing.service import IndexingService
from src.layer3_flows.indexing_flow.states import IndexingFlowContext, IndexingFlowState
from src.layer3_flows.indexing_flow.steps import ChunkingStep, FreshnessStep, IndexingStep


class IndexingFlow:
    """Execute freshness checks, chunking, and storage indexing."""

    def __init__(
        self,
        chunking_service: ChunkingService,
        indexing_service: IndexingService,
        freshness_tracker: FreshnessTracker,
    ) -> None:
        self.chunking_service = chunking_service
        self.indexing_service = indexing_service
        self.freshness_tracker = freshness_tracker
        self.freshness_step = FreshnessStep()
        self.chunking_step = ChunkingStep()
        self.indexing_step = IndexingStep()

    async def execute(
        self,
        normalized_doc: NormalizedDocument,
        chunk_precursors: list[ChunkPrecursor],
        document_checksum: str,
        config: ChunkingConfig | None = None,
    ) -> IndexingResult:
        """Index a normalized document unless freshness indicates a skip."""
        context = IndexingFlowContext(
            normalized_doc=normalized_doc,
            chunk_precursors=chunk_precursors,
            document_checksum=document_checksum,
            config=config,
        )
        try:
            context.state = IndexingFlowState.CHECKING_FRESHNESS
            await self.freshness_step.execute(self, context)
            if context.state == IndexingFlowState.SKIPPED and context.indexing_result is not None:
                return context.indexing_result

            context.state = IndexingFlowState.CHUNKING
            await self.chunking_step.execute(self, context)

            context.state = IndexingFlowState.INDEXING
            await self.indexing_step.execute(self, context)

            context.state = IndexingFlowState.COMPLETED
            return context.indexing_result
        except Exception as error:  # noqa: BLE001
            context.state = IndexingFlowState.FAILED
            context.errors.append(str(error))
            return IndexingResult(
                job_id="failed",
                document_id=normalized_doc.original_document_id,
                status=IndexStatus.FAILED,
                chunks_indexed=0,
                vector_index_time_ms=0,
                lexical_index_time_ms=0,
                total_time_ms=0,
                errors=context.errors,
            )

    async def _check_freshness(self, context: IndexingFlowContext) -> None:
        """Skip indexing when the document checksum is already current."""
        should_reindex = await self.freshness_tracker.needs_reindex(
            context.normalized_doc.original_document_id,
            context.document_checksum,
        )
        if not should_reindex:
            context.state = IndexingFlowState.SKIPPED
            context.indexing_result = IndexingResult(
                job_id="skip",
                document_id=context.normalized_doc.original_document_id,
                status=IndexStatus.COMPLETED,
                chunks_indexed=0,
                vector_index_time_ms=0,
                lexical_index_time_ms=0,
                total_time_ms=0,
            )

    async def _chunk(self, context: IndexingFlowContext) -> None:
        """Generate chunks for the normalized document."""
        context.chunking_result = await self.chunking_service.chunk(
            ChunkingRequest(
                id=f"chunk-{context.normalized_doc.id}",
                document_id=context.normalized_doc.original_document_id,
                normalized_content=context.normalized_doc.content,
                chunk_precursors=context.chunk_precursors,
                config=context.config or ChunkingConfig(),
            )
        )

    async def _index(self, context: IndexingFlowContext) -> None:
        """Index the generated chunks into storage."""
        if context.chunking_result is None:
            raise ValueError("Chunking must complete before indexing")
        document = Document.model_construct(
            id=context.normalized_doc.original_document_id,
            content=context.normalized_doc.content,
            document_type=DocumentType.UNKNOWN,
            metadata=context.normalized_doc.metadata,
            checksum=context.document_checksum,
            parser_used=None,
            parser_confidence=None,
            original_size_bytes=None,
        )
        context.indexing_result = await self.indexing_service.index_chunks(
            context.chunking_result.chunks,
            context.document_checksum,
            document=document,
        )
