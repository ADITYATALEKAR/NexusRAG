"""Integration tests for wiring validation failures."""

from pathlib import Path
import shutil

import pytest
import yaml

from src.layer0_core.errors.base import BootstrapError
from src.layer8_runtime.bootstrap.startup import BootstrapSequence


@pytest.mark.asyncio
async def test_bootstrap_fails_on_missing_required_component(tmp_path: Path) -> None:
    """Bootstrap should fail fast when a required component cannot be bound."""
    config_dir = _copy_configs(tmp_path)
    system_map_path = config_dir / "wiring" / "system-map.yaml"
    data = yaml.safe_load(system_map_path.read_text(encoding="utf-8"))
    data["components"].append(
        {
            "id": "missing_required_component",
            "component_type": "service",
            "layer": "layer2_domain",
            "required": True,
        }
    )
    system_map_path.write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(BootstrapError):
        await BootstrapSequence(config_dir=config_dir).run()


@pytest.mark.asyncio
async def test_bootstrap_fails_on_dependency_cycle(tmp_path: Path) -> None:
    """Bootstrap should fail fast on cycles."""
    config_dir = _copy_configs(tmp_path)
    system_map_path = config_dir / "wiring" / "system-map.yaml"
    data = yaml.safe_load(system_map_path.read_text(encoding="utf-8"))
    data["dependencies"].append(
        {
            "from_component": "component_registry",
            "to_component": "health_monitor",
            "link_type": "required",
        }
    )
    system_map_path.write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(BootstrapError):
        await BootstrapSequence(config_dir=config_dir).run()


def _copy_configs(tmp_path: Path) -> Path:
    """Copy the repo config directory into a temp location."""
    source = Path("configs")
    destination = tmp_path / "configs"
    shutil.copytree(source, destination)
    return destination
