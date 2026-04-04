"""Postgres metadata store backed by Neon."""

from __future__ import annotations

from datetime import datetime
import json

from src.layer1_contracts.interfaces.metadata_store import MetadataStoreInterface
from src.layer1_contracts.schemas.chunk import Chunk, ChunkLocation, ChunkMetadata
from src.layer1_contracts.schemas.document import Document, DocumentMetadata, DocumentType
from src.layer1_contracts.schemas.indexing import IndexState
from src.layer4_providers.stores.postgres.connection import connect_postgres


class PostgresMetadataStore(MetadataStoreInterface):
    """Persist document and chunk metadata in Postgres."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    async def save_chunk(self, chunk: Chunk) -> None:
        """Persist metadata for one chunk."""
        document_title = chunk.metadata.document_title
        document_type = chunk.metadata.document_type
        tags = list(chunk.metadata.tags)
        trust_score = chunk.metadata.trust_score
        with connect_postgres(self.database_url) as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    id, title, document_type, tags, trust_score, checksum, parser_used,
                    parser_confidence, original_size_bytes, ingested_at
                )
                VALUES (
                    %(id)s, %(title)s, %(document_type)s, %(tags)s::jsonb, %(trust_score)s,
                    COALESCE((SELECT checksum FROM documents WHERE id = %(id)s), NULL),
                    COALESCE((SELECT parser_used FROM documents WHERE id = %(id)s), NULL),
                    COALESCE((SELECT parser_confidence FROM documents WHERE id = %(id)s), NULL),
                    COALESCE((SELECT original_size_bytes FROM documents WHERE id = %(id)s), NULL),
                    COALESCE((SELECT ingested_at FROM documents WHERE id = %(id)s), %(ingested_at)s)
                )
                ON CONFLICT (id) DO UPDATE SET
                    title = COALESCE(EXCLUDED.title, documents.title),
                    document_type = COALESCE(EXCLUDED.document_type, documents.document_type),
                    tags = CASE
                        WHEN EXCLUDED.tags IS NULL OR EXCLUDED.tags = '[]'::jsonb THEN documents.tags
                        ELSE EXCLUDED.tags
                    END,
                    trust_score = COALESCE(EXCLUDED.trust_score, documents.trust_score)
                """,
                {
                    "id": chunk.document_id,
                    "title": document_title,
                    "document_type": document_type,
                    "tags": json.dumps(tags),
                    "trust_score": trust_score,
                    "ingested_at": chunk.created_at,
                },
            )
            connection.execute(
                """
                DELETE FROM chunks
                WHERE id = %(id)s
                """,
                {"id": chunk.id},
            )
            connection.execute(
                """
                INSERT INTO chunks (
                    id, document_id, content, document_title, document_type,
                    tags, trust_score, section_title, section_hierarchy, page_numbers,
                    token_count, created_at, embedding_model, child_chunk_ids,
                    sequence_number, parent_chunk_id, start_char, end_char, start_page, end_page
                )
                VALUES (
                    %(id)s, %(document_id)s, %(content)s, %(document_title)s, %(document_type)s,
                    %(tags)s::jsonb, %(trust_score)s, %(section_title)s, %(section_hierarchy)s::jsonb,
                    %(page_numbers)s::jsonb, %(token_count)s, %(created_at)s, %(embedding_model)s,
                    %(child_chunk_ids)s::jsonb, %(sequence_number)s, %(parent_chunk_id)s,
                    %(start_char)s, %(end_char)s, %(start_page)s, %(end_page)s
                )
                """,
                {
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "content": chunk.content,
                    "document_title": document_title,
                    "document_type": document_type,
                    "tags": json.dumps(tags),
                    "trust_score": trust_score,
                    "section_title": chunk.metadata.section_title,
                    "section_hierarchy": json.dumps(chunk.metadata.section_hierarchy),
                    "page_numbers": json.dumps(chunk.metadata.page_numbers),
                    "token_count": chunk.token_count,
                    "created_at": chunk.created_at,
                    "embedding_model": chunk.embedding_model,
                    "child_chunk_ids": json.dumps(chunk.child_chunk_ids),
                    "sequence_number": chunk.sequence_number,
                    "parent_chunk_id": chunk.parent_chunk_id,
                    "start_char": chunk.location.start_char,
                    "end_char": chunk.location.end_char,
                    "start_page": chunk.location.start_page,
                    "end_page": chunk.location.end_page,
                },
            )

    async def get_chunk(self, chunk_id: str) -> dict | None:
        """Return stored metadata for one chunk."""
        return self.get_chunk_sync(chunk_id)

    def get_chunk_sync(self, chunk_id: str) -> dict | None:
        """Return stored metadata for one chunk (synchronous)."""
        with connect_postgres(self.database_url) as connection:
            row = connection.execute(
                "SELECT * FROM chunks WHERE id = %s",
                (chunk_id,),
            ).fetchone()
        if row is None:
            return None
        return self._deserialize_chunk_row(row)

    async def list_chunks(self) -> list[Chunk]:
        """Return every stored chunk ordered by document and sequence."""
        return self.list_chunks_sync()

    def list_chunks_sync(self) -> list[Chunk]:
        """Return every stored chunk ordered by document and sequence."""
        with connect_postgres(self.database_url) as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM chunks
                ORDER BY document_id ASC, sequence_number ASC, id ASC
                """
            ).fetchall()
        return [self._row_to_chunk(row) for row in rows]

    async def list_documents(self) -> list[Document]:
        """Return every stored document."""
        return self.list_documents_sync()

    def list_documents_sync(self) -> list[Document]:
        """Return every stored document."""
        with connect_postgres(self.database_url) as connection:
            rows = connection.execute(
                """
                SELECT d.*, COALESCE(string_agg(c.content, E'\\n\\n' ORDER BY c.sequence_number), '') AS content
                FROM documents d
                LEFT JOIN chunks c ON c.document_id = d.id
                GROUP BY d.id
                ORDER BY d.ingested_at ASC, d.id ASC
                """
            ).fetchall()
        return [self._row_to_document(row) for row in rows]

    async def save_index_state(self, state: IndexState) -> None:
        """Persist index state for one document."""
        with connect_postgres(self.database_url) as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    id, checksum, indexed_at, chunk_count, embedding_model, is_stale, last_verified_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    checksum = EXCLUDED.checksum,
                    indexed_at = EXCLUDED.indexed_at,
                    chunk_count = EXCLUDED.chunk_count,
                    embedding_model = EXCLUDED.embedding_model,
                    is_stale = EXCLUDED.is_stale,
                    last_verified_at = EXCLUDED.last_verified_at
                """,
                (
                    state.document_id,
                    state.document_checksum,
                    state.indexed_at,
                    state.chunk_count,
                    state.embedding_model,
                    state.is_stale,
                    state.last_verified_at,
                ),
            )

    async def get_index_state(self, document_id: str) -> IndexState | None:
        """Return index state for one document."""
        with connect_postgres(self.database_url) as connection:
            row = connection.execute(
                """
                SELECT id, checksum, indexed_at, chunk_count, embedding_model, is_stale, last_verified_at
                FROM documents
                WHERE id = %s
                """,
                (document_id,),
            ).fetchone()
        if row is None or row.get("indexed_at") is None:
            return None
        return IndexState(
            document_id=row["id"],
            document_checksum=row["checksum"],
            indexed_at=row["indexed_at"],
            chunk_count=row["chunk_count"] or 0,
            embedding_model=row["embedding_model"] or "",
            is_stale=bool(row["is_stale"]),
            last_verified_at=row["last_verified_at"],
        )

    async def mark_stale(self, document_id: str) -> None:
        """Mark an indexed document as stale."""
        with connect_postgres(self.database_url) as connection:
            connection.execute(
                "UPDATE documents SET is_stale = TRUE WHERE id = %s",
                (document_id,),
            )

    async def get_stale_documents(self) -> list[str]:
        """Return all stale document identifiers."""
        with connect_postgres(self.database_url) as connection:
            rows = connection.execute(
                "SELECT id FROM documents WHERE is_stale = TRUE ORDER BY id ASC"
            ).fetchall()
        return [row["id"] for row in rows]

    async def delete_document(self, document_id: str) -> int:
        """Delete stored metadata for one document and return removed chunk count."""
        with connect_postgres(self.database_url) as connection:
            removed = connection.execute(
                "DELETE FROM chunks WHERE document_id = %s RETURNING id",
                (document_id,),
            ).fetchall()
            connection.execute("DELETE FROM documents WHERE id = %s", (document_id,))
        return len(removed)

    def _row_to_chunk(self, row: dict) -> Chunk:
        """Convert one chunk row into the typed contract."""
        section_hierarchy = row["section_hierarchy"] or []
        page_numbers = row["page_numbers"] or []
        child_chunk_ids = row["child_chunk_ids"] or []
        tags = row["tags"] or []
        created_at = row["created_at"] or datetime.utcnow()
        return Chunk(
            id=row["id"],
            document_id=row["document_id"],
            content=row["content"],
            location=ChunkLocation(
                start_char=row["start_char"] or 0,
                end_char=row["end_char"] or len(row["content"] or ""),
                start_page=row["start_page"],
                end_page=row["end_page"],
            ),
            sequence_number=row["sequence_number"] or 0,
            parent_chunk_id=row["parent_chunk_id"],
            child_chunk_ids=child_chunk_ids,
            metadata=ChunkMetadata(
                document_title=row["document_title"],
                document_type=row["document_type"],
                tags=tags,
                trust_score=row["trust_score"],
                section_title=row["section_title"],
                section_hierarchy=section_hierarchy,
                page_numbers=page_numbers,
            ),
            token_count=row["token_count"],
            embedding_model=row["embedding_model"],
            created_at=created_at,
        )

    def _row_to_document(self, row: dict) -> Document:
        """Convert one document row into the typed contract."""
        raw_type = row.get("document_type") or DocumentType.UNKNOWN.value
        try:
            document_type = DocumentType(raw_type)
        except ValueError:
            document_type = DocumentType.UNKNOWN
        return Document.model_construct(
            id=row["id"],
            content=row.get("content") or "",
            document_type=document_type,
            metadata=DocumentMetadata(
                title=row.get("title"),
                tags=row.get("tags") or [],
            ),
            checksum=row.get("checksum"),
            parser_used=row.get("parser_used"),
            parser_confidence=row.get("parser_confidence"),
            original_size_bytes=row.get("original_size_bytes"),
            ingested_at=row.get("ingested_at") or datetime.utcnow(),
        )

    def _deserialize_chunk_row(self, row: dict) -> dict:
        """Normalize row field names into the legacy chunk metadata mapping."""
        return {
            "chunk_id": row["id"],
            "document_id": row["document_id"],
            "content": row["content"],
            "document_title": row["document_title"],
            "document_type": row["document_type"],
            "tags": row["tags"] or [],
            "trust_score": row["trust_score"],
            "section_title": row["section_title"],
            "section_hierarchy": row["section_hierarchy"] or [],
            "page_numbers": row["page_numbers"] or [],
            "token_count": row["token_count"],
            "created_at": row["created_at"],
            "embedding_model": row["embedding_model"],
            "child_chunk_ids": row["child_chunk_ids"] or [],
            "sequence_number": row["sequence_number"],
            "parent_chunk_id": row["parent_chunk_id"],
            "start_char": row["start_char"],
            "end_char": row["end_char"],
            "start_page": row["start_page"],
            "end_page": row["end_page"],
        }
