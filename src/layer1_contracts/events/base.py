"""Base event contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseEvent(BaseModel):
    """Base event model for observability."""

    model_config = ConfigDict(extra="forbid")

    id: str
    event_type: str
    component: str
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
