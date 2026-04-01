"""Metrics middleware."""

from __future__ import annotations

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.layer5_wiring.observability.metrics import metrics


class MetricsMiddleware(BaseHTTPMiddleware):
    """Record request latency and counters for every HTTP call."""

    async def dispatch(self, request: Request, call_next):
        """Time the request and increment request counters."""
        tags = {"path": request.url.path, "method": request.method}
        with metrics.timer("http_request_duration", tags):
            response = await call_next(request)
        metrics.increment("http_requests_total", tags={"status": str(response.status_code), **tags})
        return response
