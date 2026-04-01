"""Integration tests for the Phase 8 SDK and CLI."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
import httpx
import pytest
from typer.testing import CliRunner

from cli.commands.eval import evaluate_command
from cli.commands.ingest import ingest_command
from cli.commands.query import query_command
from cli.main import app as cli_app
from sdk.async_client import AsyncRAGClient
from sdk.client import RAGClient
from sdk.models import EvalResult, IngestResult, QueryResult


def _build_sdk_app() -> FastAPI:
    app = FastAPI()

    @app.post("/answer")
    async def answer() -> dict:
        return {
            "answer_id": "ans-1",
            "query_id": "qry-1",
            "text": "VectorCore answer",
            "status": "success",
            "citations": [],
            "trace": None,
        }

    @app.post("/ingest")
    async def ingest() -> dict:
        return {
            "request_id": "req-1",
            "document_id": "doc-1",
            "status": "completed",
            "parser_used": "fallback_text",
            "parser_confidence": 0.7,
            "chunks_indexed": 3,
            "warnings": [],
            "errors": [],
            "processing_time_ms": 12,
            "indexing_job_id": "job-1",
        }

    @app.get("/health")
    @app.get("/health/")
    async def health() -> dict:
        return {"status": "healthy"}

    @app.post("/evaluate")
    async def evaluate() -> dict:
        return {
            "run_id": "eval-1",
            "dataset_id": "dataset-1",
            "retrieval_metrics": {"precision_at_k": {"1": 1.0}},
            "generation_metrics": {"faithfulness": 1.0},
            "avg_latency_ms": 10.0,
            "p95_latency_ms": 10.0,
            "p99_latency_ms": 10.0,
            "total_cost_usd": 0.01,
        }

    @app.post("/regression")
    async def regression() -> dict:
        payload = await evaluate()
        return {
            "current": payload,
            "baseline": payload,
            "regressions": [],
            "improvements": ["latency"],
            "passed": True,
        }

    @app.post("/baseline")
    async def baseline() -> dict:
        return {"status": "saved", "path": "baseline.json"}

    return app


def test_sync_sdk_client_works_with_expected_endpoints(tmp_path: Path) -> None:
    """The synchronous SDK client should support query, ingest, health, and eval."""
    sample_file = tmp_path / "sample.txt"
    sample_file.write_text("VectorCore sample", encoding="utf-8")

    with TestClient(_build_sdk_app()) as test_client:
        client = RAGClient(base_url="http://testserver")
        client._client.close()
        client._client = test_client

        query_result = client.query("What is VectorCore?")
        assert isinstance(query_result, QueryResult)
        assert query_result.answer == "VectorCore answer"

        ingest_result = client.ingest(str(sample_file))
        assert isinstance(ingest_result, IngestResult)
        assert ingest_result.chunks_indexed == 3

        health = client.health()
        assert health["status"] == "healthy"

        eval_result = client.evaluate("dataset-1")
        assert isinstance(eval_result, EvalResult)
        assert eval_result.dataset_id == "dataset-1"


@pytest.mark.asyncio
async def test_async_sdk_client_works_with_expected_endpoints(tmp_path: Path) -> None:
    """The asynchronous SDK client should support query and health."""
    sample_file = tmp_path / "sample.txt"
    sample_file.write_text("VectorCore sample", encoding="utf-8")

    transport = httpx.ASGITransport(app=_build_sdk_app())
    client = AsyncRAGClient(base_url="http://testserver")
    await client._client.aclose()
    client._client = httpx.AsyncClient(transport=transport, base_url="http://testserver")

    query_result = await client.query("What is VectorCore?")
    assert query_result.answer == "VectorCore answer"

    ingest_result = await client.ingest(str(sample_file))
    assert ingest_result.chunks_indexed == 3

    health = await client.health()
    assert health["status"] == "healthy"
    await client.close()


def test_cli_command_functions_can_query_ingest_and_evaluate(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The CLI command functions should use the SDK and complete successfully."""
    sample_file = tmp_path / "sample.txt"
    sample_file.write_text("VectorCore sample", encoding="utf-8")

    class DummyClient:
        def __init__(self, *args, **kwargs) -> None:  # noqa: D401, ARG002
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            return None

        def query(self, text: str, top_k: int = 5, include_evidence: bool = True) -> QueryResult:  # noqa: ARG002
            return QueryResult(answer_id="ans-1", query_id="qry-1", text="VectorCore answer", status="success")

        def ingest(self, file_path: str, metadata: dict | None = None) -> IngestResult:  # noqa: ARG002
            return IngestResult(
                request_id="req-1",
                document_id="doc-1",
                status="completed",
                parser_used="fallback_text",
                parser_confidence=0.7,
                chunks_indexed=3,
                processing_time_ms=10,
                indexing_job_id="job-1",
            )

        def evaluate(self, dataset_id: str) -> EvalResult:  # noqa: ARG002
            return EvalResult(
                run_id="eval-1",
                dataset_id="dataset-1",
                retrieval_metrics={"precision_at_k": {"1": 1.0}},
                generation_metrics={"faithfulness": 1.0},
                avg_latency_ms=10.0,
                p95_latency_ms=10.0,
                p99_latency_ms=10.0,
                total_cost_usd=0.01,
            )

        def regression_test(self, dataset_id: str, baseline_id: str):  # noqa: ARG002
            raise NotImplementedError

        def save_baseline(self, result, dataset: str):  # noqa: ARG002
            return {"status": "saved"}

        def health(self) -> dict:
            return {"status": "healthy"}

    monkeypatch.setattr("sdk.client.RAGClient", DummyClient)
    query_command("What is VectorCore?")
    ingest_command(str(sample_file))
    evaluate_command("dataset-1")

    captured = capsys.readouterr().out
    assert "VectorCore answer" in captured
    assert "OK" in captured
    assert "Evaluation" in captured


def test_cli_entrypoint_help_and_commands_work(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The real Typer entrypoint should expose working query, ingest, and evaluate commands."""
    sample_file = tmp_path / "sample.txt"
    sample_file.write_text("VectorCore sample", encoding="utf-8")

    class DummyClient:
        def __init__(self, *args, **kwargs) -> None:  # noqa: D401, ARG002
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            return None

        def query(self, text: str, top_k: int = 5, include_evidence: bool = False) -> QueryResult:  # noqa: ARG002
            return QueryResult(answer_id="ans-1", query_id="qry-1", text="VectorCore answer", status="success")

        def ingest(self, file_path: str, metadata: dict | None = None) -> IngestResult:  # noqa: ARG002
            return IngestResult(
                request_id="req-1",
                document_id="doc-1",
                status="completed",
                parser_used="fallback_text",
                parser_confidence=0.7,
                chunks_indexed=3,
                processing_time_ms=10,
                indexing_job_id="job-1",
            )

        def evaluate(self, dataset_id: str) -> EvalResult:  # noqa: ARG002
            return EvalResult(
                run_id="eval-1",
                dataset_id="dataset-1",
                retrieval_metrics={"precision_at_k": {"1": 1.0}},
                generation_metrics={"faithfulness": 1.0},
                avg_latency_ms=10.0,
                p95_latency_ms=10.0,
                p99_latency_ms=10.0,
                total_cost_usd=0.01,
            )

        def regression_test(self, dataset_id: str, baseline_id: str):  # noqa: ARG002
            raise NotImplementedError

        def save_baseline(self, result, dataset: str):  # noqa: ARG002
            return {"status": "saved"}

        def health(self) -> dict:
            return {"status": "healthy"}

    monkeypatch.setattr("sdk.client.RAGClient", DummyClient)
    runner = CliRunner()

    help_result = runner.invoke(cli_app, ["--help"])
    assert help_result.exit_code == 0
    assert "query" in help_result.output
    assert "ingest" in help_result.output
    assert "evaluate" in help_result.output

    query_result = runner.invoke(cli_app, ["query", "What is VectorCore?"])
    assert query_result.exit_code == 0
    assert "VectorCore answer" in query_result.output

    ingest_result = runner.invoke(cli_app, ["ingest", str(sample_file)])
    assert ingest_result.exit_code == 0
    assert "OK" in ingest_result.output

    evaluate_result = runner.invoke(cli_app, ["evaluate", "dataset-1"])
    assert evaluate_result.exit_code == 0
    assert "Evaluation" in evaluate_result.output
