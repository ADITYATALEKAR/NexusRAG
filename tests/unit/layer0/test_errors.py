"""Tests for the core error hierarchy."""

from src.layer0_core.enums.errors import ErrorCategory
from src.layer0_core.errors.base import ErrorContext, ProviderError, RateLimitError


def test_provider_error_captures_provider_id() -> None:
    """Provider errors should retain provider context."""
    error = ProviderError(
        "provider failed",
        provider_id="mock-1",
        context=ErrorContext(component="provider", operation="complete", request_id="req-1"),
    )

    assert error.provider_id == "mock-1"
    assert error.category == ErrorCategory.PROVIDER_ERROR
    assert "request_id=req-1" in str(error)


def test_rate_limit_error_exposes_retry_after() -> None:
    """Rate limit errors should expose retry timing."""
    error = RateLimitError("slow down", retry_after=2.5)

    assert error.retry_after == 2.5
    assert error.category == ErrorCategory.RATE_LIMITED
