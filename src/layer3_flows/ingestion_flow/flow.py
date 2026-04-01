"""Ingestion flow orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone

from src.layer0_core.errors.base import ValidationError
from src.layer0_core.ids.base import DocumentId
from src.layer1_contracts.schemas.document import Document, DocumentMetadata, DocumentStatus, DocumentType
from src.layer1_contracts.schemas.ingestion import IngestionRequest
from src.layer1_contracts.schemas.ingestion import IngestionResult, IngestionStatus
from src.layer1_contracts.schemas.security import SecurityDecisionType
from src.layer2_domain.ingestion.checksum import compute_checksum
from src.layer2_domain.ingestion.file_guards import FileGuard
from src.layer2_domain.normalization.chunk_preparer import ChunkPreparer
from src.layer2_domain.normalization.service import NormalizationService
from src.layer2_domain.parsing.fallback_selector import FallbackSelector
from src.layer2_domain.parsing.quality_checker import ParseQualityChecker
from src.layer2_domain.parsing.registry import ParserRegistry
from src.layer3_flows.ingestion_flow.states import FlowContext, FlowState
from src.layer3_flows.ingestion_flow.steps import (
    ChunkPreparationStep,
    NormalizationStep,
    ParsingStep,
    ValidationStep,
)


class IngestionFlow:
    """Execute validation, parsing, normalization, and chunk preparation."""

    def __init__(
        self,
        file_guard: FileGuard,
        parser_registry: ParserRegistry,
        normalization_service: NormalizationService,
        chunk_preparer: ChunkPreparer,
    ) -> None:
        self.file_guard = file_guard
        self.parser_registry = parser_registry
        self.normalization_service = normalization_service
        self.chunk_preparer = chunk_preparer
        self.quality_checker = ParseQualityChecker()
        self.fallback_selector = FallbackSelector(min_confidence=0.3)
        self.validation_step = ValidationStep()
        self.parsing_step = ParsingStep()
        self.normalization_step = NormalizationStep()
        self.chunk_preparation_step = ChunkPreparationStep()

    async def execute(self, request: IngestionRequest) -> IngestionResult:
        """Run the ingestion flow and return a typed result."""
        context = await self.execute_with_context(request)
        return self._build_result(context)

    async def execute_with_context(self, request: IngestionRequest) -> FlowContext:
        """Run the ingestion flow and return the full execution context."""
        context = FlowContext(request=request)
        try:
            context.state = FlowState.VALIDATING
            await self.validation_step.execute(self, context)

            context.state = FlowState.PARSING
            await self.parsing_step.execute(self, context)

            context.state = FlowState.NORMALIZING
            await self.normalization_step.execute(self, context)

            context.state = FlowState.PREPARING
            await self.chunk_preparation_step.execute(self, context)

            context.state = FlowState.COMPLETED
        except Exception as error:  # noqa: BLE001
            context.state = FlowState.FAILED
            context.errors.append(str(error))
        return context

    async def _validate(self, context: FlowContext) -> None:
        """Validate the input file and create the initial document."""
        decision = self.file_guard.validate(
            context.request.file_path,
            context.request.file_metadata.file_size_bytes,
        )
        if decision.decision != SecurityDecisionType.ALLOW:
            raise ValidationError(decision.reason or "File validation failed")

        checksum = compute_checksum(context.request.file_path)
        context.document = Document(
            id=DocumentId.generate().value,
            content="",
            document_type=self._get_doc_type(context.request.file_metadata.extension),
            status=DocumentStatus.PARSING,
            checksum=checksum,
            original_size_bytes=context.request.file_metadata.file_size_bytes,
            metadata=DocumentMetadata(mime_type=context.request.file_metadata.mime_type),
        )

    async def _parse(self, context: FlowContext) -> None:
        """Parse the file and update document metadata."""
        if context.document is None:
            raise ValidationError("Document must be initialized before parsing")

        parser = self.parser_registry.get_parser(context.request.file_path)
        if parser is None:
            raise ValidationError(f"No parser for: {context.request.file_path}")

        primary_result = await parser.parse(context.request.file_path)
        primary_result.document_id = context.document.id
        primary_result.confidence = self.quality_checker.assess(primary_result)

        context.parse_result = primary_result
        if self.fallback_selector.should_use_fallback(primary_result):
            fallback = self.parser_registry.get_fallback(context.request.file_path)
            if fallback is not None and fallback is not parser:
                fallback_result = await fallback.parse(context.request.file_path)
                fallback_result.document_id = context.document.id
                fallback_result.confidence = self.quality_checker.assess(fallback_result)
                context.parse_result = self.fallback_selector.select(primary_result, fallback_result)

        context.document.content = context.parse_result.raw_text
        context.document.parser_used = context.parse_result.parser_name
        context.document.parser_confidence = context.parse_result.confidence
        context.document.status = DocumentStatus.PARSED
        context.warnings.extend(context.parse_result.warnings)

    async def _normalize(self, context: FlowContext) -> None:
        """Normalize the parsed document."""
        if context.document is None or context.parse_result is None:
            raise ValidationError("Parse result must exist before normalization")
        context.normalized_doc = await self.normalization_service.normalize(
            context.parse_result,
            context.document.id,
        )
        context.document.status = DocumentStatus.NORMALIZED
        context.document.metadata = context.normalized_doc.metadata

    async def _prepare_chunks(self, context: FlowContext) -> None:
        """Prepare chunk precursors."""
        if context.document is None or context.normalized_doc is None:
            raise ValidationError("Normalized document must exist before chunk preparation")
        context.chunk_precursors = self.chunk_preparer.prepare(context.normalized_doc)
        context.document.status = DocumentStatus.CHUNKED

    def _build_result(self, context: FlowContext) -> IngestionResult:
        """Build the final flow result."""
        elapsed_ms = int((datetime.now(timezone.utc) - context.started_at).total_seconds() * 1000)
        status_map = {
            FlowState.INITIALIZED: IngestionStatus.PENDING,
            FlowState.VALIDATING: IngestionStatus.VALIDATING,
            FlowState.PARSING: IngestionStatus.PARSING,
            FlowState.NORMALIZING: IngestionStatus.NORMALIZING,
            FlowState.PREPARING: IngestionStatus.PREPARING_CHUNKS,
            FlowState.COMPLETED: IngestionStatus.COMPLETED,
            FlowState.FAILED: IngestionStatus.FAILED,
        }
        return IngestionResult(
            request_id=context.request.id,
            document_id=context.document.id if context.document else "",
            status=status_map[context.state],
            parser_used=context.parse_result.parser_name if context.parse_result else "",
            parser_confidence=context.parse_result.confidence if context.parse_result else 0.0,
            page_count=context.normalized_doc.page_count if context.normalized_doc else 0,
            word_count=context.normalized_doc.word_count if context.normalized_doc else 0,
            chunk_count=len(context.chunk_precursors or []),
            errors=context.errors,
            warnings=context.warnings,
            processing_time_ms=elapsed_ms,
        )

    def _get_doc_type(self, extension: str) -> DocumentType:
        """Map file extensions to document types."""
        return {
            ".pdf": DocumentType.PDF,
            ".docx": DocumentType.DOCX,
            ".doc": DocumentType.DOCX,
            ".txt": DocumentType.TXT,
            ".md": DocumentType.MD,
            ".html": DocumentType.HTML,
            ".csv": DocumentType.CSV,
            ".json": DocumentType.JSON,
        }.get(extension.lower(), DocumentType.UNKNOWN)
