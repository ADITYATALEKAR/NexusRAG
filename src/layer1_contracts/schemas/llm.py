"""LLM request and response contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MessageRole(str, Enum):
    """Chat message roles."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """One chat message."""

    model_config = ConfigDict(extra="forbid")

    role: MessageRole
    content: str


class LLMConfig(BaseModel):
    """LLM generation settings."""

    model_config = ConfigDict(extra="forbid")

    model: str
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1, le=100000)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    stop_sequences: list[str] = Field(default_factory=list)


class LLMRequest(BaseModel):
    """Request for an LLM completion."""

    model_config = ConfigDict(extra="forbid")

    id: str
    messages: list[Message] = Field(..., min_length=1)
    config: LLMConfig
    preferred_provider: str | None = None
    fallback_allowed: bool = True
    timeout_seconds: float = Field(default=60.0, gt=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LLMUsage(BaseModel):
    """LLM token accounting."""

    model_config = ConfigDict(extra="forbid")

    prompt_tokens: int = Field(..., ge=0)
    completion_tokens: int = Field(..., ge=0)
    total_tokens: int = Field(..., ge=0)

    @model_validator(mode="after")
    def validate_total_tokens(self) -> "LLMUsage":
        """Ensure total_tokens is internally consistent."""
        expected = self.prompt_tokens + self.completion_tokens
        if self.total_tokens != expected:
            raise ValueError("total_tokens must equal prompt_tokens + completion_tokens")
        return self


class LLMResponse(BaseModel):
    """Response from an LLM provider."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    content: str
    provider: str
    model: str
    usage: LLMUsage
    latency_ms: int = Field(..., ge=0)
    finish_reason: str
    failover_occurred: bool = False
    providers_attempted: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
