"""Shared telemetry middleware."""

from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.layer5_wiring.observability.logging import logger, request_id_var, trace_id_var
from src.layer5_wiring.observability.metrics import metrics
from src.layer5_wiring.observability.tracing import tracer


class TelemetryMiddleware(BaseHTTPMiddleware):
    """Combined telemetry middleware for interfaces that want one wrapper."""

    async def dispatch(self, request: Request, call_next):
        """Instrument the request with logging, tracing, and metrics."""
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_var.set(request_id)
        request.state.request_id = request_id
        logger.info(
            "request_started",
            component="api",
            operation=f"{request.method} {request.url.path}",
            path=request.url.path,
            method=request.method,
        )

        with tracer.span(f"{request.method} {request.url.path}") as span:
            trace_id_var.set(span.trace_id)
            started = time.perf_counter()
            with metrics.timer(
                "http_request_duration",
                {"path": request.url.path, "method": request.method},
            ):
                response = await call_next(request)
            duration_ms = int((time.perf_counter() - started) * 1000)
            metrics.increment("http_requests_total", tags={"status": str(response.status_code)})
            span.attributes["status_code"] = response.status_code
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Trace-ID"] = span.trace_id
            logger.log_request(
                operation=f"{request.method} {request.url.path}",
                duration_ms=duration_ms,
                status=str(response.status_code),
                path=request.url.path,
                method=request.method,
            )
            return response
