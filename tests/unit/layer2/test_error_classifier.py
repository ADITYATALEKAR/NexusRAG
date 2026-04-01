"""Tests for error classification."""

from src.layer0_core.enums.errors import ErrorCategory, RetryDecision
from src.layer0_core.errors.base import ProviderError, RAGBaseError, RateLimitError, TimeoutError
from src.layer2_domain.failover.error_classifier import ErrorClassifier


def test_error_classifier_maps_known_errors() -> None:
    """Known provider errors should map to the expected decisions."""
    assert ErrorClassifier.classify(RateLimitError("limited")) == (
        ErrorCategory.RATE_LIMITED,
        RetryDecision.COOLDOWN_FAILOVER,
    )
    assert ErrorClassifier.classify(TimeoutError("slow", timeout_seconds=1.0)) == (
        ErrorCategory.TIMEOUT,
        RetryDecision.FAILOVER,
    )
    assert ErrorClassifier.classify(ProviderError("bad", provider_id="mock")) == (
        ErrorCategory.PROVIDER_ERROR,
        RetryDecision.FAILOVER,
    )


def test_error_classifier_handles_transient_errors() -> None:
    """Transient base errors should back off and retry."""
    error = RAGBaseError("transient", category=ErrorCategory.TRANSIENT)

    assert ErrorClassifier.classify(error) == (
        ErrorCategory.TRANSIENT,
        RetryDecision.RETRY_BACKOFF,
    )
