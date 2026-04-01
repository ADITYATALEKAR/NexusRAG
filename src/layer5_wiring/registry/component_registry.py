"""Component registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from src.layer0_core.enums.wiring import ComponentStatus
from src.layer0_core.errors.base import WiringError


@dataclass
class ComponentInfo:
    """Registered component metadata."""

    id: str
    component_type: str
    layer: str
    instance: Any
    status: ComponentStatus = ComponentStatus.REGISTERED
    required: bool = False
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ComponentRegistry:
    """Central registry for system components."""

    def __init__(self) -> None:
        self._components: dict[str, ComponentInfo] = {}

    def register(
        self,
        component_id: str,
        instance: Any,
        component_type: str,
        layer: str,
        required: bool = False,
    ) -> ComponentInfo:
        """Register a component."""
        if component_id in self._components:
            raise WiringError(f"Component already registered: {component_id}")
        info = ComponentInfo(
            id=component_id,
            instance=instance,
            component_type=component_type,
            layer=layer,
            required=required,
            status=ComponentStatus.FAILED if instance is None and required else ComponentStatus.REGISTERED,
        )
        self._components[component_id] = info
        return info

    def get(self, component_id: str) -> ComponentInfo | None:
        """Return a registered component."""
        return self._components.get(component_id)

    def get_instance(self, component_id: str) -> Any | None:
        """Return a component instance."""
        component = self.get(component_id)
        return component.instance if component else None

    def get_by_type(self, component_type: str) -> list[ComponentInfo]:
        """Return components by type."""
        return [component for component in self._components.values() if component.component_type == component_type]

    def get_by_layer(self, layer: str) -> list[ComponentInfo]:
        """Return components by layer."""
        return [component for component in self._components.values() if component.layer == layer]

    def get_required(self) -> list[ComponentInfo]:
        """Return required components."""
        return [component for component in self._components.values() if component.required]

    def set_status(self, component_id: str, status: ComponentStatus) -> None:
        """Update component status."""
        component = self.get(component_id)
        if component is None:
            raise WiringError(f"Unknown component: {component_id}")
        component.status = status

    def all_required_ready(self) -> bool:
        """Return whether all required components are ready."""
        return all(component.status == ComponentStatus.READY for component in self.get_required())

    def all_components(self) -> list[ComponentInfo]:
        """Return all registered components."""
        return list(self._components.values())
