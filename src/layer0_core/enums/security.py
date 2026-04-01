"""Security-related enums."""

from enum import Enum


class SecurityMode(str, Enum):
    """Security operating modes."""

    STRICT = "strict"
    STANDARD = "standard"
    PERMISSIVE = "permissive"


class AuditOutcome(str, Enum):
    """Audit result categories."""

    ALLOWED = "allowed"
    DENIED = "denied"
    SANITIZED = "sanitized"
    ERROR = "error"
