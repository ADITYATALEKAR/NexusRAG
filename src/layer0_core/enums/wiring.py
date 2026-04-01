"""Wiring and validation enums."""

from enum import Enum


class ComponentStatus(str, Enum):
    """Component lifecycle states."""

    REGISTERED = "registered"
    INITIALIZING = "initializing"
    READY = "ready"
    FAILED = "failed"
    DISABLED = "disabled"


class LinkType(str, Enum):
    """Types of links in the dependency graph."""

    REQUIRED = "required"
    OPTIONAL = "optional"
    FALLBACK = "fallback"
    MONITORING = "monitoring"


class ValidationSeverity(str, Enum):
    """Validation issue severity."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
