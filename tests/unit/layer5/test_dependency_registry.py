"""Tests for the dependency registry."""

from src.layer0_core.enums.wiring import LinkType
from src.layer5_wiring.registry.dependency_registry import DependencyRegistry


def test_dependency_registry_topological_sort_orders_dependencies() -> None:
    """Dependencies should produce a stable topological order."""
    registry = DependencyRegistry()
    registry.add("service", "database", LinkType.REQUIRED)
    registry.add("api", "service", LinkType.REQUIRED)

    ordered, cycles = registry.topological_sort()

    assert cycles == []
    assert ordered.index("database") < ordered.index("service") < ordered.index("api")


def test_dependency_registry_detects_cycles() -> None:
    """Cycles should be surfaced explicitly."""
    registry = DependencyRegistry()
    registry.add("a", "b", LinkType.REQUIRED)
    registry.add("b", "a", LinkType.REQUIRED)

    cycles = registry.detect_cycles()

    assert cycles
