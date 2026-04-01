"""Integration tests for API runtime storage resolution."""

from __future__ import annotations

from pathlib import Path

from apps.api.runtime_storage import load_storage_runtime


def test_storage_runtime_defaults_to_project_data_dir(tmp_path: Path, monkeypatch) -> None:
    """The storage runtime should default to a local data directory under the project root."""
    for name in [
        "NEXUSRAG_DATA_DIR",
        "DATA_DIR",
        "QDRANT_URL",
        "QDRANT_API_KEY",
        "NEXUSRAG_METADATA_DB_PATH",
        "NEXUSRAG_LEXICAL_DB_PATH",
        "NEXUSRAG_GRAPH_PATH",
        "NEXUSRAG_VECTOR_COMPRESSION_STATE_PATH",
        "NEXUSRAG_UPLOAD_DIR",
    ]:
        monkeypatch.delenv(name, raising=False)

    config = load_storage_runtime(project_root=tmp_path)

    assert config.data_dir == tmp_path / "data"
    assert config.metadata_db_path == tmp_path / "data" / "metadata.db"
    assert config.lexical_db_path == tmp_path / "data" / "lexical.db"
    assert config.graph_path == tmp_path / "data" / "graph.pkl"
    assert config.vector_compression_state_path == tmp_path / "data" / "vector_compression.npz"
    assert config.upload_dir == tmp_path / "data" / "uploads"
    assert config.qdrant_url == str(tmp_path / "data" / "qdrant")


def test_storage_runtime_uses_external_vector_store_envs(tmp_path: Path, monkeypatch) -> None:
    """The storage runtime should honor explicit env-driven overrides for Northflank-style deploys."""
    monkeypatch.setenv("NEXUSRAG_DATA_DIR", str(tmp_path / "runtime"))
    monkeypatch.setenv("QDRANT_URL", "https://qdrant.example.com:6333")
    monkeypatch.setenv("QDRANT_API_KEY", "example-qdrant-key")

    config = load_storage_runtime(project_root=tmp_path)

    assert config.data_dir == tmp_path / "runtime"
    assert config.qdrant_url == "https://qdrant.example.com:6333"
    assert config.qdrant_api_key == "example-qdrant-key"
    assert config.metadata_db_path == tmp_path / "runtime" / "metadata.db"
