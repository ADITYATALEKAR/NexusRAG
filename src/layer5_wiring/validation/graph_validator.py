"""Dependency graph validation."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.layer0_core.enums.wiring import ComponentStatus, ValidationSeverity
from src.layer5_wiring.registry.component_registry import ComponentRegistry
from src.layer5_wiring.registry.dependency_registry import DependencyRegistry


@dataclass
class ValidationIssue:
    """One validation issue."""

    severity: ValidationSeverity
    component: str | None
    message: str
    rule: str


@dataclass
class ValidationResult:
    """Graph validation output."""

    valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)


class GraphValidator:
    """Validate the wiring graph."""

    LAYER_ORDER = [
        "layer0_core",
        "layer1_contracts",
        "layer2_domain",
        "layer3_flows",
        "layer4_providers",
        "layer5_wiring",
        "layer6_security",
        "layer7_interfaces",
        "layer8_runtime",
    ]

    def __init__(self, component_registry: ComponentRegistry, dependency_registry: DependencyRegistry) -> None:
        self.component_registry = component_registry
        self.dependency_registry = dependency_registry

    def validate(self) -> ValidationResult:
        """Run required component, dependency, cycle, and layer checks."""
        issues: list[ValidationIssue] = []
        issues.extend(self._validate_required_components())
        issues.extend(self._validate_dependency_existence())
        issues.extend(self._validate_cycles())
        issues.extend(self._validate_layer_rules())
        valid = not any(issue.severity == ValidationSeverity.ERROR for issue in issues)
        return ValidationResult(valid=valid, issues=issues)

    def _validate_required_components(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for component in self.component_registry.get_required():
            if component.instance is None:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        component=component.id,
                        message="Required component is not bound to an instance",
                        rule="required_instance",
                    )
                )
            if component.status == ComponentStatus.FAILED:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        component=component.id,
                        message="Required component is in failed state",
                        rule="required_failed",
                    )
                )
        return issues

    def _validate_dependency_existence(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for dependency in self.dependency_registry.all():
            if self.component_registry.get(dependency.from_component) is None:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        component=dependency.from_component,
                        message=f"Dependency source is not registered: {dependency.from_component}",
                        rule="dependency_source_exists",
                    )
                )
            if self.component_registry.get(dependency.to_component) is None:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        component=dependency.from_component,
                        message=f"Dependency target is not registered: {dependency.to_component}",
                        rule="dependency_target_exists",
                    )
                )
        return issues

    def _validate_cycles(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for cycle in self.dependency_registry.detect_cycles():
            cycle_label = " -> ".join(cycle)
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    component=cycle[0] if cycle else None,
                    message=f"Cycle detected: {cycle_label}",
                    rule="acyclic_graph",
                )
            )
        return issues

    def _validate_layer_rules(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        layer_index = {layer: index for index, layer in enumerate(self.LAYER_ORDER)}
        for dependency in self.dependency_registry.all():
            source = self.component_registry.get(dependency.from_component)
            target = self.component_registry.get(dependency.to_component)
            if source is None or target is None:
                continue
            if layer_index.get(source.layer, -1) < layer_index.get(target.layer, -1):
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        component=source.id,
                        message=(
                            f"Layer rule violation: {source.layer} cannot depend on {target.layer}"
                        ),
                        rule="layer_dependency_direction",
                    )
                )
        return issues
