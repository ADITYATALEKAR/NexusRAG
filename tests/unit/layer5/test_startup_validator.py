"""Tests for the startup validator."""

import pytest

from src.layer0_core.enums.wiring import LinkType
from src.layer0_core.errors.base import BootstrapError
from src.layer5_wiring.registry.component_registry import ComponentRegistry
from src.layer5_wiring.registry.dependency_registry import DependencyRegistry
from src.layer5_wiring.validation.startup_validator import StartupValidator


def test_startup_validator_raises_in_strict_mode() -> None:
    """Strict mode should raise on invalid graphs."""
    component_registry = ComponentRegistry()
    dependency_registry = DependencyRegistry()
    component_registry.register(
        "component-a",
        instance=object(),
        component_type="service",
        layer="layer2_domain",
        required=True,
    )
    dependency_registry.add("component-a", "missing", LinkType.REQUIRED)

    with pytest.raises(BootstrapError):
        StartupValidator(component_registry, dependency_registry, strict_mode=True).validate()
