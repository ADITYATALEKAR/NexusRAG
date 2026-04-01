"""Observability contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LogLevel(str, Enum):
    """Supported log levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogEntry(BaseModel):
    """Structured application log entry."""

    model_config = ConfigDict(extra="forbid")

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    level: LogLevel
    message: str
    request_id: str | None = None
    trace_id: str | None = None
    span_id: str | None = None
    component: str
    operation: str
    duration_ms: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MetricPoint(BaseModel):
    """Single metrics data point."""

    model_config = ConfigDict(extra="forbid")

    name: str
    value: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags: dict[str, str] = Field(default_factory=dict)
    metric_type: str = "gauge"


class SpanContext(BaseModel):
    """Tracing span metadata."""

    model_config = ConfigDict(extra="forbid")

    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    operation: str
    service: str
    start_time: datetime
    end_time: datetime | None = None
    status: str = "ok"
    attributes: dict[str, Any] = Field(default_factory=dict)


class CostRecord(BaseModel):
    """Recorded provider cost for one request."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
