"""Core error hierarchy."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from src.layer0_core.enums.errors import ErrorCategory


@dataclass
class ErrorContext:
    """Structured context attached to errors."""

    request_id: str | None = None
    component: str | None = None
    operation: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


class RAGBaseError(Exception):
    """Base for all system errors."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: ErrorContext | None = None,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.category = category
        self.context = context or ErrorContext()
        self.cause = cause

    def __str__(self) -> str:
        """Return a compact human-readable error string."""
        parts = [self.message, f"category={self.category.value}"]
        if self.context.component:
            parts.append(f"component={self.context.component}")
        if self.context.operation:
            parts.append(f"operation={self.context.operation}")
        if self.context.request_id:
            parts.append(f"request_id={self.context.request_id}")
        return " | ".join(parts)


class ConfigurationError(RAGBaseError):
    """Raised for invalid configuration."""


class WiringError(RAGBaseError):
    """Raised for wiring and dependency errors."""


class ProviderError(RAGBaseError):
    """Raised for provider execution failures."""

    def __init__(self, message: str, provider_id: str, **kwargs: Any) -> None:
        super().__init__(message, category=ErrorCategory.PROVIDER_ERROR, **kwargs)
        self.provider_id = provider_id


class RateLimitError(RAGBaseError):
    """Raised when a provider returns a rate limit."""

    def __init__(self, message: str, retry_after: float | None = None, **kwargs: Any) -> None:
        super().__init__(message, category=ErrorCategory.RATE_LIMITED, **kwargs)
        self.retry_after = retry_after


class TimeoutError(RAGBaseError):
    """Raised when an operation times out."""

    def __init__(self, message: str, timeout_seconds: float, **kwargs: Any) -> None:
        super().__init__(message, category=ErrorCategory.TIMEOUT, **kwargs)
        self.timeout_seconds = timeout_seconds


class ValidationError(RAGBaseError):
    """Raised when validation fails."""


class SecurityError(RAGBaseError):
    """Raised for security policy violations."""


class BootstrapError(RAGBaseError):
    """Raised when bootstrap validation or initialization fails."""

    def __init__(self, message: str, failed_components: list[str], **kwargs: Any) -> None:
        super().__init__(message, **kwargs)
        self.failed_components = failed_components
