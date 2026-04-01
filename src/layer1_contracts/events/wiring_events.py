"""Wiring-related events."""

from __future__ import annotations

from pydantic import ConfigDict

from src.layer1_contracts.events.base import BaseEvent


class ComponentRegisteredEvent(BaseEvent):
    """Emitted when a component is registered."""

    model_config = ConfigDict(extra="forbid")

    component_id: str
    component_type: str
    layer: str


class WiringValidationEvent(BaseEvent):
    """Emitted after wiring validation."""

    model_config = ConfigDict(extra="forbid")

    valid: bool
    issue_count: int
