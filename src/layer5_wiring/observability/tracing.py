"""In-memory tracing manager."""

from __future__ import annotations

from contextvars import ContextVar, Token
from datetime import datetime, timezone
import uuid

from src.layer1_contracts.schemas.observability import SpanContext
from src.layer5_wiring.observability.logging import span_id_var, trace_id_var

current_span: ContextVar[SpanContext | None] = ContextVar("current_span", default=None)


class TracingManager:
    """Capture spans with parent-child relationships."""

    def __init__(self, service_name: str = "rag-system") -> None:
        self.service_name = service_name
        self._spans: list[SpanContext] = []
        self._tokens: dict[str, tuple[Token, Token, Token]] = {}

    def start_span(self, operation: str, parent: SpanContext | None = None) -> SpanContext:
        """Create and activate a new span."""
        active_parent = parent or current_span.get()
        span = SpanContext(
            trace_id=active_parent.trace_id if active_parent else str(uuid.uuid4()),
            span_id=uuid.uuid4().hex[:16],
            parent_span_id=active_parent.span_id if active_parent else None,
            operation=operation,
            service=self.service_name,
            start_time=datetime.now(timezone.utc),
        )
        current_token = current_span.set(span)
        trace_token = trace_id_var.set(span.trace_id)
        span_token = span_id_var.set(span.span_id)
        self._tokens[span.span_id] = (current_token, trace_token, span_token)
        return span

    def end_span(
        self,
        span: SpanContext,
        status: str = "ok",
        attributes: dict | None = None,
    ) -> None:
        """Complete the span and restore the previous active span."""
        span.end_time = datetime.now(timezone.utc)
        span.status = status
        if attributes:
            span.attributes.update(attributes)
        self._spans.append(span)

        tokens = self._tokens.pop(span.span_id, None)
        if tokens is not None:
            current_span.reset(tokens[0])
            trace_id_var.reset(tokens[1])
            span_id_var.reset(tokens[2])

    def span(self, operation: str) -> "SpanContextManager":
        """Return a context manager for a traced operation."""
        return SpanContextManager(self, operation)

    def export_spans(self, limit: int | None = None) -> list[dict]:
        """Export captured spans as dictionaries."""
        items = self._spans[-limit:] if limit is not None else self._spans
        return [span.model_dump() for span in items]

    def clear(self) -> None:
        """Clear captured spans for test isolation."""
        self._spans.clear()
        self._tokens.clear()


class SpanContextManager:
    """Context manager wrapper around the tracing manager."""

    def __init__(self, tracer: TracingManager, operation: str) -> None:
        self.tracer = tracer
        self.operation = operation
        self.span: SpanContext | None = None

    def __enter__(self) -> SpanContext:
        """Start and return the active span."""
        self.span = self.tracer.start_span(self.operation)
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Finish the active span."""
        if self.span is None:
            return
        status = "error" if exc_type else "ok"
        self.tracer.end_span(self.span, status=status)


tracer = TracingManager()
