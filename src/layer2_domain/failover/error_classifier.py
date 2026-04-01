"""Provider error classification."""

from __future__ import annotations

from src.layer0_core.enums.errors import ErrorCategory, RetryDecision
from src.layer0_core.errors.base import ProviderError, RAGBaseError, RateLimitError, TimeoutError


class ErrorClassifier:
    """Map exceptions to categories and retry decisions."""

    @staticmethod
    def classify(error: Exception) -> tuple[ErrorCategory, RetryDecision]:
        """Map an exception to a retry strategy."""
        if isinstance(error, RateLimitError):
            return ErrorCategory.RATE_LIMITED, RetryDecision.COOLDOWN_FAILOVER
        if isinstance(error, TimeoutError):
            return ErrorCategory.TIMEOUT, RetryDecision.FAILOVER
        if isinstance(error, ProviderError):
            return ErrorCategory.PROVIDER_ERROR, RetryDecision.FAILOVER
        if isinstance(error, RAGBaseError):
            if error.category == ErrorCategory.TRANSIENT:
                return ErrorCategory.TRANSIENT, RetryDecision.RETRY_BACKOFF
            if error.category in {
                ErrorCategory.AUTHENTICATION,
                ErrorCategory.INVALID_REQUEST,
                ErrorCategory.QUOTA_EXCEEDED,
                ErrorCategory.CLIENT_ERROR,
            }:
                return error.category, RetryDecision.ABORT
            return error.category, RetryDecision.FAILOVER
        return ErrorCategory.UNKNOWN, RetryDecision.FAILOVER
