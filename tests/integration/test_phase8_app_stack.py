"""Integration tests for the real Phase 8 app stack."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from apps.api.main import app


def test_main_app_health_and_ingest_stack_work(tmp_path: Path) -> None:
    """The real app should start, ingest a document, and retrieve it."""
    sample_file = tmp_path / "vectorcore-phase8.txt"
    unique_term = "VectorCorePhase8UniqueAlpha"
    sample_file.write_text(
        f"{unique_term}\n\nVectorCore Phase 8 ingestion integration test document.",
        encoding="utf-8",
    )

    with TestClient(app) as client:
        liveness = client.get("/health/liveness")
        assert liveness.status_code == 200

        with sample_file.open("rb") as handle:
            ingest = client.post(
                "/ingest",
                files={"file": (sample_file.name, handle, "text/plain")},
                data={"metadata": "{}"},
            )
        assert ingest.status_code == 200
        assert ingest.json()["chunks_indexed"] >= 1

        retrieval = client.post(
            "/retrieval/retrieve",
            json={"query": unique_term, "top_k": 1, "rerank": False},
        )
        assert retrieval.status_code == 200
        assert retrieval.json()["candidates"]
