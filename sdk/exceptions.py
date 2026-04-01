"""Exceptions raised by the SDK."""


class RAGError(Exception):
    """Base SDK error."""


class AuthError(RAGError):
    """Authentication failure."""


class RateLimitError(RAGError):
    """Rate limiting failure."""
