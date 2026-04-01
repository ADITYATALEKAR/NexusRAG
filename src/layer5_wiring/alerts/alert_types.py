"""Alert types used by monitoring and startup."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class AlertType(str, Enum):
    """High-level alert categories."""

    WIRING = "wiring"
    PROVIDER = "provider"
    SECURITY = "security"
    BOOTSTRAP = "bootstrap"


@dataclass(frozen=True)
class Alert:
    """One alert event."""

    alert_type: AlertType
    severity: AlertSeverity
    message: str
    component_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
