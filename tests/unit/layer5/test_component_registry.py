"""Tests for the component registry."""

from src.layer0_core.enums.wiring import ComponentStatus
from src.layer5_wiring.registry.component_registry import ComponentRegistry


def test_component_registry_tracks_required_components() -> None:
    """Required components should be discoverable and status-aware."""
    registry = ComponentRegistry()
    registry.register("component-a", instance=object(), component_type="service", layer="layer2_domain", required=True)
    registry.set_status("component-a", ComponentStatus.READY)

    assert registry.get("component-a") is not None
    assert registry.all_required_ready() is True
