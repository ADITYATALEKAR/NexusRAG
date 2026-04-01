"""Error categorization enums."""

from enum import Enum


class ErrorCategory(str, Enum):
    """High-level error categories for retry and failover decisions."""

    TRANSIENT = "transient"
    RATE_LIMITED = "rate_limited"
    PROVIDER_ERROR = "provider_error"
    CLIENT_ERROR = "client_error"
    TIMEOUT = "timeout"
    AUTHENTICATION = "authentication"
    QUOTA_EXCEEDED = "quota_exceeded"
    INVALID_REQUEST = "invalid_request"
    UNKNOWN = "unknown"


class RetryDecision(str, Enum):
    """Retry strategies available to the failover layer."""

    RETRY_SAME = "retry_same"
    RETRY_BACKOFF = "retry_backoff"
    FAILOVER = "failover"
    ABORT = "abort"
    COOLDOWN_FAILOVER = "cooldown_failover"
