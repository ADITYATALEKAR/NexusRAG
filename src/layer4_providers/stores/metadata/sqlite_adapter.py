"""SQLite metadata store."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import sqlite3

from src.layer1_contracts.schemas.chunk import Chunk
from src.layer1_contracts.schemas.chunk import ChunkLocation, ChunkMetadata
from src.layer1_contracts.schemas.document import Document, DocumentMetadata, DocumentType
from src.layer1_contracts.schemas.indexing import IndexState


class SQLiteMetadataStore:
    """Persist chunk metadata and index state in SQLite."""

    def __init__(self, db_path: str = "data/metadata.db") -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    async def save_chunk(self, chunk: Chunk) -> None:
        """Persist metadata for one chunk."""
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO chunk_metadata
                (
                    chunk_id, document_id, content, document_title, document_type,
                    tags, trust_score, section_title, section_hierarchy, page_numbers,
                    token_count, created_at, embedding_model, child_chunk_ids,
                    sequence_number, parent_chunk_id, start_char, end_char, start_page, end_page
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk.id,
                    chunk.document_id,
                    chunk.content,
                    chunk.metadata.document_title,
                    chunk.metadata.document_type,
                    json.dumps(chunk.metadata.tags),
                    chunk.metadata.trust_score,
                    chunk.metadata.section_title,
                    json.dumps(chunk.metadata.section_hierarchy),
                    json.dumps(chunk.metadata.page_numbers),
                    chunk.token_count,
                    chunk.created_at.isoformat(),
                    chunk.embedding_model,
                    json.dumps(chunk.child_chunk_ids),
                    chunk.sequence_number,
                    chunk.parent_chunk_id,
                    chunk.location.start_char,
                    chunk.location.end_char,
                    chunk.location.start_page,
                    chunk.location.end_page,
                ),
            )
            connection.commit()

    async def get_chunk(self, chunk_id: str) -> dict | None:
        """Return stored metadata for one chunk."""
        return self.get_chunk_sync(chunk_id)

    def get_chunk_sync(self, chunk_id: str) -> dict | None:
        """Return stored metadata for one chunk synchronously."""
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.execute(
                "SELECT * FROM chunk_metadata WHERE chunk_id = ?",
                (chunk_id,),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        result = dict(row)
        result["tags"] = json.loads(result["tags"]) if result["tags"] else []
        result["section_hierarchy"] = (
            json.loads(result["section_hierarchy"]) if result["section_hierarchy"] else []
        )
        result["page_numbers"] = json.loads(result["page_numbers"]) if result["page_numbers"] else []
        result["child_chunk_ids"] = (
            json.loads(result["child_chunk_ids"]) if result["child_chunk_ids"] else []
        )
        return result

    async def list_chunks(self) -> list[Chunk]:
        """Return every stored chunk ordered for downstream graph building."""
        return self.list_chunks_sync()

    def list_chunks_sync(self) -> list[Chunk]:
        """Return every stored chunk ordered for downstream graph building."""
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT *
                FROM chunk_metadata
                ORDER BY document_id ASC, sequence_number ASC, chunk_id ASC
                """
            ).fetchall()

        chunks: list[Chunk] = []
        for row in rows:
            tags = json.loads(row["tags"]) if row["tags"] else []
            hierarchy = json.loads(row["section_hierarchy"]) if row["section_hierarchy"] else []
            page_numbers = json.loads(row["page_numbers"]) if row["page_numbers"] else []
            child_chunk_ids = json.loads(row["child_chunk_ids"]) if row["child_chunk_ids"] else []
            start_char = row["start_char"] if row["start_char"] is not None else 0
            end_char = row["end_char"] if row["end_char"] is not None else len(row["content"] or "")

            chunks.append(
                Chunk(
                    id=row["chunk_id"],
                    document_id=row["document_id"],
                    content=row["content"],
                    location=ChunkLocation(
                        start_char=start_char,
                        end_char=end_char,
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
                        section_hierarchy=hierarchy,
                        page_numbers=page_numbers,
                    ),
                    token_count=row["token_count"],
                    embedding_model=row["embedding_model"],
                    created_at=(
                        datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else datetime.utcnow()
                    ),
                )
            )
        return chunks

    async def list_documents(self) -> list[Document]:
        """Return synthesized documents for graph construction and diagnostics."""
        return self.list_documents_sync()

    def list_documents_sync(self) -> list[Document]:
        """Return synthesized documents for graph construction and diagnostics."""
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT *
                FROM chunk_metadata
                ORDER BY document_id ASC, sequence_number ASC, chunk_id ASC
                """
            ).fetchall()

        documents: list[Document] = []
        current_document_id: str | None = None
        content_parts: list[str] = []
        current_metadata: sqlite3.Row | None = None

        def flush_document() -> None:
            nonlocal current_document_id, content_parts, current_metadata
            if current_document_id is None or current_metadata is None:
                return

            document_type_raw = current_metadata["document_type"] or DocumentType.UNKNOWN.value
            try:
                document_type = DocumentType(document_type_raw)
            except ValueError:
                document_type = DocumentType.UNKNOWN

            tags = json.loads(current_metadata["tags"]) if current_metadata["tags"] else []
            metadata = DocumentMetadata(
                title=current_metadata["document_title"],
                tags=tags,
            )
            documents.append(
                Document.model_construct(
                    id=current_document_id,
                    content="\n\n".join(part for part in content_parts if part),
                    document_type=document_type,
                    metadata=metadata,
                    checksum=None,
                    parser_used=None,
                    parser_confidence=None,
                    original_size_bytes=None,
                    ingested_at=datetime.utcnow(),
                )
            )
            current_document_id = None
            content_parts = []
            current_metadata = None

        for row in rows:
            if current_document_id is None:
                current_document_id = row["document_id"]
                current_metadata = row
            if row["document_id"] != current_document_id:
                flush_document()
                current_document_id = row["document_id"]
                current_metadata = row
            content_parts.append(row["content"])

        flush_document()
        return documents

    async def save_index_state(self, state: IndexState) -> None:
        """Persist index state for one document."""
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO index_state
                (
                    document_id, checksum, indexed_at, chunk_count,
                    embedding_model, is_stale, last_verified_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    state.document_id,
                    state.document_checksum,
                    state.indexed_at.isoformat(),
                    state.chunk_count,
                    state.embedding_model,
                    1 if state.is_stale else 0,
                    state.last_verified_at.isoformat() if state.last_verified_at else None,
                ),
            )
            connection.commit()

    async def get_index_state(self, document_id: str) -> IndexState | None:
        """Return index state for one document."""
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.execute(
                "SELECT * FROM index_state WHERE document_id = ?",
                (document_id,),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        return IndexState(
            document_id=row["document_id"],
            document_checksum=row["checksum"],
            indexed_at=datetime.fromisoformat(row["indexed_at"]),
            chunk_count=row["chunk_count"],
            embedding_model=row["embedding_model"],
            is_stale=bool(row["is_stale"]),
            last_verified_at=(
                datetime.fromisoformat(row["last_verified_at"])
                if row["last_verified_at"]
                else None
            ),
        )

    async def mark_stale(self, document_id: str) -> None:
        """Mark an indexed document as stale."""
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                "UPDATE index_state SET is_stale = 1 WHERE document_id = ?",
                (document_id,),
            )
            connection.commit()

    async def get_stale_documents(self) -> list[str]:
        """Return all stale document ids."""
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.execute("SELECT document_id FROM index_state WHERE is_stale = 1")
            return [row[0] for row in cursor.fetchall()]

    async def delete_document(self, document_id: str) -> int:
        """Delete all stored metadata for one document and return the removed chunk count."""
        return self.delete_document_sync(document_id)

    def delete_document_sync(self, document_id: str) -> int:
        """Delete all stored metadata for one document and return the removed chunk count."""
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.execute(
                "DELETE FROM chunk_metadata WHERE document_id = ?",
                (document_id,),
            )
            removed_chunks = int(cursor.rowcount or 0)
            connection.execute(
                "DELETE FROM index_state WHERE document_id = ?",
                (document_id,),
            )
            connection.commit()
        return removed_chunks

    def _init_db(self) -> None:
        """Create metadata and index state tables."""
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chunk_metadata (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    document_title TEXT,
                    document_type TEXT,
                    tags TEXT,
                    trust_score REAL,
                    section_title TEXT,
                    section_hierarchy TEXT,
                    page_numbers TEXT,
                    token_count INTEGER,
                    created_at TEXT,
                    embedding_model TEXT,
                    child_chunk_ids TEXT,
                    sequence_number INTEGER,
                    parent_chunk_id TEXT,
                    start_char INTEGER,
                    end_char INTEGER,
                    start_page INTEGER,
                    end_page INTEGER
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS index_state (
                    document_id TEXT PRIMARY KEY,
                    checksum TEXT NOT NULL,
                    indexed_at TEXT NOT NULL,
                    chunk_count INTEGER,
                    embedding_model TEXT,
                    is_stale INTEGER DEFAULT 0,
                    last_verified_at TEXT
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_chunk_document_id ON chunk_metadata (document_id)"
            )
            existing_columns = {
                row[1] for row in connection.execute("PRAGMA table_info(chunk_metadata)").fetchall()
            }
            column_definitions = {
                "document_title": "TEXT",
                "document_type": "TEXT",
                "tags": "TEXT",
                "trust_score": "REAL",
                "section_hierarchy": "TEXT",
                "child_chunk_ids": "TEXT",
                "sequence_number": "INTEGER",
                "parent_chunk_id": "TEXT",
                "start_char": "INTEGER",
                "end_char": "INTEGER",
                "start_page": "INTEGER",
                "end_page": "INTEGER",
            }
            for column_name, column_type in column_definitions.items():
                if column_name not in existing_columns:
                    connection.execute(
                        f"ALTER TABLE chunk_metadata ADD COLUMN {column_name} {column_type}"
                    )
            connection.commit()


MetadataStore = SQLiteMetadataStore
