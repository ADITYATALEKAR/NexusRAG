"""Tracing middleware."""

from __future__ import annotations

import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.layer5_wiring.observability.logging import request_id_var, trace_id_var
from src.layer5_wiring.observability.tracing import tracer


class TracingMiddleware(BaseHTTPMiddleware):
    """Attach request and trace identifiers to every HTTP request."""

    async def dispatch(self, request: Request, call_next):
        """Start a root span and propagate correlation headers."""
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_var.set(request_id)
        request.state.request_id = request_id

        with tracer.span(f"{request.method} {request.url.path}") as span:
            trace_id_var.set(span.trace_id)
            response = await call_next(request)
            span.attributes["status_code"] = response.status_code
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Trace-ID"] = span.trace_id
            return response
