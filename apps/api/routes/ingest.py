"""Document ingestion endpoint for CLI and SDK use."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from pydantic import BaseModel, ConfigDict, Field

from apps.api.runtime_services import build_runtime_stores
from apps.api.runtime_storage import load_storage_runtime
from src.layer1_contracts.schemas.chunking import ChunkingConfig, ChunkingStrategy
from src.layer1_contracts.schemas.indexing import IndexStatus
from src.layer2_domain.chunking.service import ChunkingService
from src.layer2_domain.indexing.freshness import FreshnessTracker
from src.layer2_domain.indexing.service import IndexingService
from src.layer2_domain.ingestion.service import IngestionService
from src.layer2_domain.normalization.chunk_preparer import ChunkPreparer
from src.layer2_domain.normalization.section_detector import SectionDetector
from src.layer2_domain.normalization.service import NormalizationService
from src.layer2_domain.parsing.registry import ParserRegistry
from src.layer3_flows.indexing_flow.flow import IndexingFlow
from src.layer3_flows.ingestion_flow.flow import IngestionFlow
from src.layer4_providers.embeddings.mock.adapter import MockEmbedder
from src.layer4_providers.parsers.registry import build_default_parsers
from src.layer8_runtime.config.loader import ConfigLoader

router = APIRouter()


class IngestResponse(BaseModel):
    """Response payload for a completed ingestion and indexing run."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    document_id: str
    status: str
    parser_used: str
    parser_confidence: float = Field(ge=0.0, le=1.0)
    chunks_indexed: int
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    processing_time_ms: int
    indexing_job_id: str


@dataclass
class IngestRuntime:
    """Cached runtime for the ingestion endpoint."""

    ingestion_service: IngestionService
    ingestion_flow: IngestionFlow
    indexing_flow: IndexingFlow
    chunking_config: ChunkingConfig
    upload_dir: Path


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    request: Request,
    file: UploadFile = File(...),
    metadata: str | None = Form(default=None),
) -> IngestResponse:
    """Ingest, normalize, chunk, and index one uploaded document."""
    runtime = _get_or_build_ingest_runtime(request)
    saved_path = await _save_upload(runtime.upload_dir, file)

    try:
        parsed_metadata = json.loads(metadata) if metadata else {}
        if not isinstance(parsed_metadata, dict):
            raise ValueError("metadata form field must be a JSON object")
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    context = await runtime.ingestion_flow.execute_with_context(
        runtime.ingestion_service.create_request(
            file_path=str(saved_path),
            options=parsed_metadata,
            request_id=getattr(request.state, "request_id", None),
        )
    )
    ingestion_result = runtime.ingestion_flow._build_result(context)

    if context.normalized_doc is None or context.chunk_precursors is None or context.document is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ingestion_result.errors or ["Document ingestion failed"],
        )

    indexing_result = await runtime.indexing_flow.execute(
        normalized_doc=context.normalized_doc,
        chunk_precursors=context.chunk_precursors,
        document_checksum=context.document.checksum or "",
        config=runtime.chunking_config,
    )
    _invalidate_cached_runtimes(request)

    errors = [*ingestion_result.errors, *indexing_result.errors]
    combined_status = (
        "completed"
        if indexing_result.status == IndexStatus.COMPLETED and not errors
        else indexing_result.status.value
    )
    return IngestResponse(
        request_id=ingestion_result.request_id,
        document_id=ingestion_result.document_id,
        status=combined_status,
        parser_used=ingestion_result.parser_used,
        parser_confidence=ingestion_result.parser_confidence,
        chunks_indexed=indexing_result.chunks_indexed or ingestion_result.chunk_count,
        warnings=ingestion_result.warnings,
        errors=errors,
        processing_time_ms=ingestion_result.processing_time_ms + indexing_result.total_time_ms,
        indexing_job_id=indexing_result.job_id,
    )


def _get_or_build_ingest_runtime(request: Request) -> IngestRuntime:
    """Return the cached ingestion runtime or build it lazily."""
    runtime = getattr(request.app.state, "ingest_runtime", None)
    if runtime is not None:
        return runtime

    config_dir = Path(__file__).resolve().parents[3] / "configs"
    loader = ConfigLoader(config_dir=config_dir)
    chunking_raw = loader.load_yaml("chunking/chunking.yaml").get("chunking", {})

    parser_registry = ParserRegistry()
    for name, (parser, priority) in build_default_parsers().items():
        parser_registry.register(name, parser, priority)

    project_root = config_dir.parent
    storage = load_storage_runtime(project_root=project_root)
    ingestion_service = IngestionService()
    embed_dimensions = 384 if storage.database_url else 32
    embedder = MockEmbedder(dimensions=embed_dimensions)
    stores = build_runtime_stores(storage, embed_dimensions=embedder.dimensions)
    runtime = IngestRuntime(
        ingestion_service=ingestion_service,
        ingestion_flow=IngestionFlow(
            file_guard=ingestion_service.file_guard,
            parser_registry=parser_registry,
            normalization_service=NormalizationService(section_detector=SectionDetector()),
            chunk_preparer=ChunkPreparer(),
        ),
        indexing_flow=IndexingFlow(
            chunking_service=ChunkingService(default_config=_build_chunking_config(chunking_raw)),
            indexing_service=IndexingService(
                embedder=embedder,
                vector_store=stores.vector_store,
                lexical_store=stores.lexical_store,
                metadata_store=stores.metadata_store,
            ),
            freshness_tracker=FreshnessTracker(stores.metadata_store),
        ),
        chunking_config=_build_chunking_config(chunking_raw),
        upload_dir=storage.upload_dir,
    )
    request.app.state.ingest_runtime = runtime
    return runtime


async def _save_upload(upload_dir: Path, upload: UploadFile) -> Path:
    """Persist an uploaded file into the local data directory."""
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(upload.filename or "upload.bin").suffix
    target_path = upload_dir / f"{uuid.uuid4().hex}{suffix}"
    with target_path.open("wb") as output_handle:
        shutil.copyfileobj(upload.file, output_handle)
    await upload.close()
    return target_path


def _invalidate_cached_runtimes(request: Request) -> None:
    """Drop cached retrieval and answer runtimes so new index state is reloaded."""
    for state_name in [
        "retrieval_service",
        "retrieval_flow",
        "answer_runtime",
        "answer_flow",
        "query_runtime",
        "routed_query_flow",
        "evaluation_runtime",
    ]:
        if hasattr(request.app.state, state_name):
            delattr(request.app.state, state_name)


def _build_chunking_config(raw: dict) -> ChunkingConfig:
    """Convert the chunking YAML file into a typed config."""
    return ChunkingConfig(
        strategy=ChunkingStrategy(str(raw.get("default_strategy", "semantic"))),
        target_size=int(raw.get("target_size", 512)),
        min_size=int(raw.get("min_size", 64)),
        max_size=int(raw.get("max_size", 1024)),
        overlap=int(raw.get("overlap", 64)),
        preserve_sentences=bool(raw.get("preserve_sentences", True)),
        preserve_paragraphs=bool(raw.get("preserve_paragraphs", True)),
    )
