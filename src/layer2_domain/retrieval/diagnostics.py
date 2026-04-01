"""Diagnostics caching for retrieval operations."""

from __future__ import annotations

from collections import OrderedDict

from src.layer1_contracts.schemas.retrieval import RetrievalDiagnostics


class RetrievalDiagnosticsStore:
    """In-memory cache of recent retrieval diagnostics."""

    def __init__(self, max_entries: int = 256) -> None:
        self.max_entries = max_entries
        self._cache: OrderedDict[str, RetrievalDiagnostics] = OrderedDict()

    def put(self, diagnostics: RetrievalDiagnostics) -> None:
        """Store diagnostics for a query, evicting the oldest entry when needed."""
        self._cache[diagnostics.query_id] = diagnostics
        self._cache.move_to_end(diagnostics.query_id)
        while len(self._cache) > self.max_entries:
            self._cache.popitem(last=False)

    def get(self, query_id: str) -> RetrievalDiagnostics | None:
        """Return diagnostics for a query id if cached."""
        diagnostics = self._cache.get(query_id)
        if diagnostics is None:
            return None
        self._cache.move_to_end(query_id)
        return diagnostics

    def list_recent(self, limit: int = 20) -> list[RetrievalDiagnostics]:
        """Return the most recent diagnostics first."""
        return list(reversed(list(self._cache.values())[-limit:]))
