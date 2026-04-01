"""Startup validator."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.layer0_core.enums.wiring import ValidationSeverity
from src.layer0_core.errors.base import BootstrapError
from src.layer5_wiring.registry.component_registry import ComponentRegistry
from src.layer5_wiring.registry.dependency_registry import DependencyRegistry
from src.layer5_wiring.validation.graph_validator import GraphValidator, ValidationIssue


@dataclass
class StartupValidationResult:
    """Startup validation result."""

    valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    ordered_components: list[str] = field(default_factory=list)
    cycle_components: list[str] = field(default_factory=list)


class StartupValidator:
    """Validate startup wiring in strict or warning mode."""

    def __init__(
        self,
        component_registry: ComponentRegistry,
        dependency_registry: DependencyRegistry,
        strict_mode: bool = True,
    ) -> None:
        self.component_registry = component_registry
        self.dependency_registry = dependency_registry
        self.strict_mode = strict_mode

    def validate(self) -> StartupValidationResult:
        """Validate the graph and optionally raise on error."""
        graph_result = GraphValidator(
            component_registry=self.component_registry,
            dependency_registry=self.dependency_registry,
        ).validate()
        ordered, cycle_components = self.dependency_registry.topological_sort()
        valid = graph_result.valid and len(cycle_components) == 0
        result = StartupValidationResult(
            valid=valid,
            issues=graph_result.issues,
            ordered_components=ordered,
            cycle_components=cycle_components,
        )
        if self.strict_mode and not valid:
            failed_components = sorted(
                {
                    issue.component
                    for issue in graph_result.issues
                    if issue.component and issue.severity == ValidationSeverity.ERROR
                }
            )
            failed_components.extend(component for component in cycle_components if component not in failed_components)
            raise BootstrapError("Startup validation failed", failed_components=failed_components)
        return result
