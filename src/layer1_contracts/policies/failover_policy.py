"""Failover policy contract."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FailoverPolicy(BaseModel):
    """Configured provider chain and cooldown behavior."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    max_providers: int = Field(default=5, ge=1)
    cooldown_enabled: bool = True
    cooldown_duration_seconds: int = Field(default=60, ge=1)
    max_cooldown_duration_seconds: int = Field(default=300, ge=1)
    consecutive_failures_threshold: int = Field(default=3, ge=1)
