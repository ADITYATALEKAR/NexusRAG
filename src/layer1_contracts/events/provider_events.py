"""Provider-related events."""

from __future__ import annotations

from pydantic import ConfigDict

from src.layer1_contracts.events.base import BaseEvent


class ProviderAttemptedEvent(BaseEvent):
    """Emitted when a provider attempt occurs."""

    model_config = ConfigDict(extra="forbid")

    provider_id: str
    success: bool


class ProviderCooldownEvent(BaseEvent):
    """Emitted when a provider enters cooldown."""

    model_config = ConfigDict(extra="forbid")

    provider_id: str
    duration_seconds: int
    reason: str
