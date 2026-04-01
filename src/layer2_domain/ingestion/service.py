"""Ingestion request preparation."""

from __future__ import annotations

from pathlib import Path

from src.layer0_core.errors.base import ValidationError
from src.layer0_core.ids.base import RequestId
from src.layer1_contracts.schemas.ingestion import IngestionRequest
from src.layer1_contracts.schemas.security import SecurityDecisionType
from src.layer2_domain.ingestion.file_guards import FileGuard
from src.layer2_domain.ingestion.metadata_extractor import MetadataExtractor


class IngestionService:
    """Prepare validated ingestion requests from file paths."""

    def __init__(
        self,
        file_guard: FileGuard | None = None,
        metadata_extractor: MetadataExtractor | None = None,
    ) -> None:
        self.file_guard = file_guard or FileGuard()
        self.metadata_extractor = metadata_extractor or MetadataExtractor()

    def create_request(
        self,
        file_path: str,
        options: dict | None = None,
        request_id: str | None = None,
    ) -> IngestionRequest:
        """Create a validated ingestion request from a file path."""
        path = Path(file_path)
        if not path.exists():
            raise ValidationError(f"File not found: {file_path}")

        file_metadata = self.metadata_extractor.extract(file_path)
        decision = self.file_guard.validate(file_path, file_metadata.file_size_bytes)
        if decision.decision != SecurityDecisionType.ALLOW:
            raise ValidationError(decision.reason or "File validation failed")

        return IngestionRequest(
            id=RequestId.generate().value,
            file_path=str(path),
            file_metadata=file_metadata,
            options=options or {},
            request_id=request_id,
        )
