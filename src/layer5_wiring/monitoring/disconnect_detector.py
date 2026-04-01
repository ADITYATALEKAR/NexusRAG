"""Disconnect detection helpers."""

from __future__ import annotations

from src.layer5_wiring.registry.component_registry import ComponentRegistry
from src.layer5_wiring.registry.dependency_registry import DependencyRegistry


class DisconnectDetector:
    """Detect broken dependency links."""

    def __init__(self, component_registry: ComponentRegistry, dependency_registry: DependencyRegistry) -> None:
        self.component_registry = component_registry
        self.dependency_registry = dependency_registry

    def detect(self) -> list[str]:
        """Return human-readable disconnect descriptions."""
        issues: list[str] = []
        for dependency in self.dependency_registry.all():
            if self.component_registry.get(dependency.from_component) is None:
                issues.append(f"Missing source component: {dependency.from_component}")
            if self.component_registry.get(dependency.to_component) is None:
                issues.append(f"Missing target component: {dependency.to_component}")
        return issues
