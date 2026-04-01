"""Runtime storage helpers for API services."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class StorageRuntimeConfig:
    """Resolved storage configuration for API runtime services."""

    data_dir: Path
    upload_dir: Path
    metadata_db_path: Path
    lexical_db_path: Path
    graph_path: Path
    vector_compression_state_path: Path
    qdrant_url: str
    qdrant_api_key: str | None
    qdrant_collection: str


def load_storage_runtime(project_root: Path | None = None) -> StorageRuntimeConfig:
    """Resolve local file paths and external vector store settings from env."""
    resolved_root = project_root or Path(__file__).resolve().parents[2]
    default_data_dir = resolved_root / "data"

    data_dir = Path(os.getenv("NEXUSRAG_DATA_DIR") or os.getenv("DATA_DIR") or default_data_dir)
    upload_dir = Path(os.getenv("NEXUSRAG_UPLOAD_DIR") or (data_dir / "uploads"))
    metadata_db_path = Path(os.getenv("NEXUSRAG_METADATA_DB_PATH") or (data_dir / "metadata.db"))
    lexical_db_path = Path(os.getenv("NEXUSRAG_LEXICAL_DB_PATH") or (data_dir / "lexical.db"))
    graph_path = Path(os.getenv("NEXUSRAG_GRAPH_PATH") or (data_dir / "graph.pkl"))
    vector_compression_state_path = Path(
        os.getenv("NEXUSRAG_VECTOR_COMPRESSION_STATE_PATH") or (data_dir / "vector_compression.npz")
    )
    qdrant_url = (
        os.getenv("QDRANT_URL")
        or os.getenv("NEXUSRAG_QDRANT_URL")
        or str(data_dir / "qdrant")
    )
    qdrant_api_key = os.getenv("QDRANT_API_KEY") or os.getenv("NEXUSRAG_QDRANT_API_KEY")
    qdrant_collection = os.getenv("NEXUSRAG_QDRANT_COLLECTION", "retrieval_chunks")

    for path in [data_dir, upload_dir, metadata_db_path.parent, lexical_db_path.parent, graph_path.parent]:
        path.mkdir(parents=True, exist_ok=True)

    return StorageRuntimeConfig(
        data_dir=data_dir,
        upload_dir=upload_dir,
        metadata_db_path=metadata_db_path,
        lexical_db_path=lexical_db_path,
        graph_path=graph_path,
        vector_compression_state_path=vector_compression_state_path,
        qdrant_url=qdrant_url,
        qdrant_api_key=qdrant_api_key,
        qdrant_collection=qdrant_collection,
    )
