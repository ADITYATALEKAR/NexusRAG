"""Tests for the graph validator."""

from src.layer0_core.enums.wiring import LinkType
from src.layer5_wiring.registry.component_registry import ComponentRegistry
from src.layer5_wiring.registry.dependency_registry import DependencyRegistry
from src.layer5_wiring.validation.graph_validator import GraphValidator


def test_graph_validator_flags_missing_targets_and_layer_violations() -> None:
    """Validator should catch missing dependencies and upward layer links."""
    component_registry = ComponentRegistry()
    dependency_registry = DependencyRegistry()
    component_registry.register(
        "contracts",
        instance=object(),
        component_type="module",
        layer="layer1_contracts",
        required=True,
    )
    component_registry.register(
        "runtime",
        instance=object(),
        component_type="module",
        layer="layer8_runtime",
        required=True,
    )
    dependency_registry.add("contracts", "runtime", LinkType.REQUIRED)
    dependency_registry.add("runtime", "missing", LinkType.REQUIRED)

    result = GraphValidator(component_registry, dependency_registry).validate()

    assert result.valid is False
    rules = {issue.rule for issue in result.issues}
    assert "layer_dependency_direction" in rules
    assert "dependency_target_exists" in rules
