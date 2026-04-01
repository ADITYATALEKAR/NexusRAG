"""Health reporting contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class HealthStatus(str, Enum):
    """Health status values."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentHealth(BaseModel):
    """Health status for one component."""

    model_config = ConfigDict(extra="forbid")

    component_id: str
    component_type: str
    status: HealthStatus
    message: str | None = None
    last_check: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    consecutive_failures: int = 0
    latency_ms: int | None = None


class ProviderHealth(BaseModel):
    """Health and availability for one provider."""

    model_config = ConfigDict(extra="forbid")

    provider_id: str
    provider_type: str
    vendor: str
    status: HealthStatus
    is_available: bool = True
    is_in_cooldown: bool = False
    cooldown_until: datetime | None = None
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_latency_ms: float | None = None
    last_error: str | None = None


class SystemHealth(BaseModel):
    """Aggregate system health."""

    model_config = ConfigDict(extra="forbid")

    status: HealthStatus
    components: list[ComponentHealth] = Field(default_factory=list)
    providers: list[ProviderHealth] = Field(default_factory=list)
    total_components: int = 0
    healthy_components: int = 0
    degraded_components: int = 0
    unhealthy_components: int = 0
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
