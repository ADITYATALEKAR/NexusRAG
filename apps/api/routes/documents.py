"""Document management endpoints for the frontend workspace."""

from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field

from apps.api.runtime_storage import load_storage_runtime
from src.layer4_providers.stores.metadata.sqlite_adapter import SQLiteMetadataStore
from src.layer4_providers.stores.qdrant.adapter import QdrantAdapter
from src.layer4_providers.stores.sqlite_fts.adapter import SQLiteFTSAdapter

router = APIRouter(prefix="/documents")


class DocumentSummary(BaseModel):
    """Frontend-friendly summary for one indexed document."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    status: str = "completed"
    size_label: str
    uploaded_at: str
    parser_used: str | None = None
    chunks_indexed: int = Field(default=0, ge=0)


class DocumentDeleteResponse(BaseModel):
    """Delete response for one document."""

    model_config = ConfigDict(extra="forbid")

    ok: bool = True
    id: str
    removed_chunks: int = Field(default=0, ge=0)


@router.get("", response_model=list[DocumentSummary])
async def list_documents() -> list[DocumentSummary]:
    """Return all indexed documents known to the metadata store."""
    storage = load_storage_runtime()
    metadata_store = SQLiteMetadataStore(db_path=str(storage.metadata_db_path))
    documents = metadata_store.list_documents_sync()
    chunk_counts = Counter(chunk.document_id for chunk in metadata_store.list_chunks_sync())

    results: list[DocumentSummary] = []
    for document in documents:
        content_bytes = len(document.content.encode("utf-8"))
        results.append(
            DocumentSummary(
                id=document.id,
                name=document.metadata.title or document.id,
                status="completed",
                size_label=_to_size_label(content_bytes),
                uploaded_at=document.ingested_at.isoformat(),
                parser_used=document.parser_used,
                chunks_indexed=chunk_counts.get(document.id, 0),
            )
        )
    return results


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(document_id: str, request: Request) -> DocumentDeleteResponse:
    """Delete one indexed document from metadata, lexical, and vector stores."""
    storage = load_storage_runtime()
    metadata_store = SQLiteMetadataStore(db_path=str(storage.metadata_db_path))
    chunks = [chunk for chunk in metadata_store.list_chunks_sync() if chunk.document_id == document_id]
    chunk_ids = [chunk.id for chunk in chunks]

    removed_chunks = metadata_store.delete_document_sync(document_id)

    if chunk_ids:
        lexical_store = SQLiteFTSAdapter(db_path=str(storage.lexical_db_path))
        vector_store = QdrantAdapter(
            url=storage.qdrant_url,
            api_key=storage.qdrant_api_key,
            collection=storage.qdrant_collection,
            dimensions=32,
        )
        for chunk_id in chunk_ids:
            await lexical_store.delete(chunk_id)
        await vector_store.delete(chunk_ids)

    _invalidate_cached_runtimes(request)
    return DocumentDeleteResponse(id=document_id, removed_chunks=removed_chunks)

def _to_size_label(size_bytes: int) -> str:
    """Format a human-readable size label for the frontend."""
    if size_bytes < 1024 * 1024:
        return f"{max(1, round(size_bytes / 1024))} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def _invalidate_cached_runtimes(request: Request) -> None:
    """Drop cached app runtimes so document changes are visible immediately."""
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
