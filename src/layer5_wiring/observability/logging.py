"""Structured logging utilities."""

from __future__ import annotations

from contextvars import ContextVar
import logging
import sys

import structlog

request_id_var: ContextVar[str] = ContextVar("request_id", default="")
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")
span_id_var: ContextVar[str] = ContextVar("span_id", default="")


class StructuredLogger:
    """JSON structured logger with request and trace correlation."""

    def __init__(self, service_name: str = "rag-system") -> None:
        self.service_name = service_name
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.add_log_level,
                self._add_context,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
            cache_logger_on_first_use=True,
        )
        self._logger = structlog.get_logger()

    def _add_context(self, _logger, _method_name: str, event_dict: dict) -> dict:
        """Inject correlation and service context into every log event."""
        event_dict["service"] = self.service_name
        event_dict.setdefault("request_id", request_id_var.get())
        event_dict.setdefault("trace_id", trace_id_var.get())
        event_dict.setdefault("span_id", span_id_var.get())
        return event_dict

    def debug(self, message: str, **kwargs) -> None:
        """Write a debug log event."""
        self._logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Write an info log event."""
        self._logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Write a warning log event."""
        self._logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Write an error log event."""
        self._logger.error(message, **kwargs)

    def log_request(self, operation: str, duration_ms: int, status: str, **kwargs) -> None:
        """Write a normalized request-completion event."""
        self.info(
            "request_completed",
            component="api",
            operation=operation,
            duration_ms=duration_ms,
            status=status,
            **kwargs,
        )

    def log_provider_call(
        self,
        provider: str,
        model: str,
        tokens: int,
        latency_ms: int,
        success: bool,
    ) -> None:
        """Write a normalized provider-call event."""
        self.info(
            "provider_call",
            component="llm",
            operation="complete",
            provider=provider,
            model=model,
            tokens=tokens,
            latency_ms=latency_ms,
            success=success,
        )

    @staticmethod
    def clear_context() -> None:
        """Clear correlation context after a request finishes."""
        request_id_var.set("")
        trace_id_var.set("")
        span_id_var.set("")


logger = StructuredLogger()
