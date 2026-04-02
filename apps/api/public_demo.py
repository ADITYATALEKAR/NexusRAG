"""Public demo quota helpers for the hosted NexusRAG deployment."""

from __future__ import annotations

from dataclasses import dataclass
import os
from threading import Lock

from fastapi import Request

from src.layer4_providers.stores.postgres.connection import connect_postgres

SESSION_HEADER = "X-NexusRAG-Session"
DEFAULT_QUERY_LIMIT = 2


@dataclass(frozen=True)
class TrialUsage:
    """Usage counters for the public hosted trial."""

    limit: int
    used: int
    allowed: bool

    @property
    def remaining(self) -> int:
        """Return how many hosted trial queries remain."""
        return max(self.limit - self.used, 0)


class PublicDemoUsageTracker:
    """Track public hosted trial usage in Neon or in-memory fallback storage."""

    def __init__(self, database_url: str | None, limit: int = DEFAULT_QUERY_LIMIT) -> None:
        self.database_url = database_url
        self.limit = max(limit, 0)
        self._lock = Lock()
        self._memory_usage: dict[str, int] = {}
        self._table_ready = False

    def consume(self, session_id: str) -> TrialUsage:
        """Reserve one hosted trial query for the given session identifier."""
        if self.limit <= 0:
            return TrialUsage(limit=0, used=0, allowed=False)

        normalized_session_id = _normalize_session_id(session_id)
        if self.database_url:
            return self._consume_postgres(normalized_session_id)
        return self._consume_memory(normalized_session_id)

    def _ensure_postgres_table(self) -> None:
        if self._table_ready or not self.database_url:
            return
        with connect_postgres(self.database_url) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS public_demo_usage (
                    session_id TEXT PRIMARY KEY,
                    query_count INTEGER NOT NULL DEFAULT 0,
                    last_used_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        self._table_ready = True

    def _consume_postgres(self, session_id: str) -> TrialUsage:
        self._ensure_postgres_table()
        assert self.database_url is not None
        with connect_postgres(self.database_url) as connection:
            cursor = connection.execute(
                """
                INSERT INTO public_demo_usage (session_id, query_count, last_used_at)
                VALUES (%s, 1, NOW())
                ON CONFLICT (session_id) DO UPDATE
                SET
                    query_count = public_demo_usage.query_count + 1,
                    last_used_at = NOW()
                WHERE public_demo_usage.query_count < %s
                RETURNING query_count
                """,
                (session_id, self.limit),
            )
            row = cursor.fetchone()
            if row:
                return TrialUsage(limit=self.limit, used=int(row["query_count"]), allowed=True)

            current_row = connection.execute(
                "SELECT query_count FROM public_demo_usage WHERE session_id = %s",
                (session_id,),
            ).fetchone()
            used = int(current_row["query_count"]) if current_row else self.limit
            return TrialUsage(limit=self.limit, used=used, allowed=False)

    def _consume_memory(self, session_id: str) -> TrialUsage:
        with self._lock:
            used = self._memory_usage.get(session_id, 0)
            if used >= self.limit:
                return TrialUsage(limit=self.limit, used=used, allowed=False)
            used += 1
            self._memory_usage[session_id] = used
            return TrialUsage(limit=self.limit, used=used, allowed=True)


def public_demo_enabled() -> bool:
    """Return whether the hosted public demo mode is active."""
    return os.getenv("NEXUSRAG_PUBLIC_DEMO_MODE", "false").lower() == "true"


def public_query_limit() -> int:
    """Return the hosted public query limit."""
    return int(os.getenv("NEXUSRAG_PUBLIC_QUERY_LIMIT", str(DEFAULT_QUERY_LIMIT)))


def should_enforce_public_demo_limit(request: Request) -> bool:
    """Hosted trial applies only to unauthenticated public traffic."""
    if not public_demo_enabled():
        return False
    return not bool(request.headers.get("X-API-Key"))


def resolve_session_id(request: Request) -> str:
    """Resolve a stable session identifier for hosted public usage."""
    header_value = request.headers.get(SESSION_HEADER)
    if header_value:
        return _normalize_session_id(header_value)

    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return _normalize_session_id(forwarded_for.split(",")[0])

    client_host = request.client.host if request.client else None
    if client_host:
        return _normalize_session_id(client_host)

    return "anonymous-session"


def build_quota_message(limit: int) -> str:
    """Return the hosted trial exhaustion message shown in the UI."""
    return (
        f"Hosted free use includes {limit} questions. "
        "Switch to Bring Your Own API for unlimited usage."
    )


def _normalize_session_id(value: str) -> str:
    cleaned = value.strip()
    return cleaned[:128] if cleaned else "anonymous-session"
