"""Security contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SecurityDecisionType(str, Enum):
    """Allowed security decisions."""

    ALLOW = "allow"
    DENY = "deny"
    SANITIZE = "sanitize"
    RATE_LIMIT = "rate_limit"
    AUDIT_ONLY = "audit_only"


class ThreatCategory(str, Enum):
    """Threat categories detected by baseline guards."""

    NONE = "none"
    INJECTION = "injection"
    PROMPT_INJECTION = "prompt_injection"
    OVERSIZED = "oversized"
    MALFORMED = "malformed"
    RATE_ABUSE = "rate_abuse"
    FORBIDDEN_CONTENT = "forbidden_content"


class SecurityDecision(BaseModel):
    """Result of a security check."""

    model_config = ConfigDict(extra="forbid")

    decision: SecurityDecisionType
    threat_category: ThreatCategory = ThreatCategory.NONE
    reason: str | None = None
    rule_triggered: str | None = None
    sanitized: bool = False
    modifications: list[str] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditEvent(BaseModel):
    """Audit event record."""

    model_config = ConfigDict(extra="forbid")

    id: str
    event_type: str
    request_id: str | None = None
    session_id: str | None = None
    component: str
    action: str
    outcome: str
    input_summary: str | None = None
    error_type: str | None = None
    error_message: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
