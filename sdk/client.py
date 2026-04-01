"""Synchronous SDK client."""

from __future__ import annotations

import json
from pathlib import Path

import httpx

from sdk.exceptions import AuthError, RAGError, RateLimitError
from sdk.models import EvalResult, IngestResult, QueryResult, RegressionTestResult


class RAGClient:
    """Synchronous client for the RAG API."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: str | None = None, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout, headers=self._headers())

    def _headers(self) -> dict[str, str]:
        """Build request headers."""
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def _handle_response(self, response: httpx.Response) -> dict:
        """Raise typed errors for non-success responses."""
        if response.status_code in {401, 403}:
            raise AuthError("Invalid or missing API key")
        if response.status_code == 429:
            retry = response.headers.get("Retry-After", "60")
            raise RateLimitError(f"Rate limited. Retry after {retry}s")
        if response.status_code >= 400:
            raise RAGError(f"API error: {response.status_code} - {response.text}")
        return response.json()

    def query(self, text: str, top_k: int = 5, include_evidence: bool = True) -> QueryResult:
        """Generate an answer for a query."""
        response = self._client.post(
            f"{self.base_url}/answer",
            json={
                "query": text,
                "top_k": top_k,
                "require_citations": include_evidence,
            },
        )
        return QueryResult(**self._handle_response(response))

    def ingest(self, file_path: str, metadata: dict | None = None) -> IngestResult:
        """Upload and ingest a document."""
        with Path(file_path).open("rb") as file_handle:
            files = {"file": (Path(file_path).name, file_handle)}
            data = {"metadata": json.dumps(metadata or {})}
            response = self._client.post(f"{self.base_url}/ingest", files=files, data=data)
        return IngestResult(**self._handle_response(response))

    def health(self) -> dict:
        """Return system health."""
        response = self._client.get(f"{self.base_url}/health")
        return self._handle_response(response)

    def evaluate(self, dataset_id: str) -> EvalResult:
        """Run an evaluation dataset."""
        response = self._client.post(f"{self.base_url}/evaluate", params={"dataset_id": dataset_id})
        return EvalResult(**self._handle_response(response))

    def regression_test(self, dataset_id: str, baseline_id: str) -> RegressionTestResult:
        """Run regression testing against a saved baseline."""
        response = self._client.post(
            f"{self.base_url}/regression",
            params={"dataset_id": dataset_id, "baseline_id": baseline_id},
        )
        return RegressionTestResult(**self._handle_response(response))

    def save_baseline(self, result: EvalResult, baseline_id: str) -> dict:
        """Save an evaluation result as a baseline."""
        response = self._client.post(
            f"{self.base_url}/baseline",
            params={"baseline_id": baseline_id},
            json=result.model_dump(mode="json"),
        )
        return self._handle_response(response)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> "RAGClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()
