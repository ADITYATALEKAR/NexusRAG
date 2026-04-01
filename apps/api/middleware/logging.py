"""Request logging middleware."""

from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.layer5_wiring.observability.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log request lifecycle with correlation fields."""

    async def dispatch(self, request: Request, call_next):
        """Write start and completion logs for the request."""
        request_id = getattr(request.state, "request_id", "") or request.headers.get(
            "X-Request-ID",
            str(uuid.uuid4()),
        )
        started = time.perf_counter()
        operation = f"{request.method} {request.url.path}"
        logger.info(
            "request_started",
            component="api",
            operation=operation,
            request_id=request_id,
            path=request.url.path,
            method=request.method,
        )
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - started) * 1000)
        logger.log_request(
            operation=operation,
            duration_ms=duration_ms,
            status=str(response.status_code),
            request_id=request_id,
            trace_id=response.headers.get("X-Trace-ID", ""),
            path=request.url.path,
            method=request.method,
        )
        return response
