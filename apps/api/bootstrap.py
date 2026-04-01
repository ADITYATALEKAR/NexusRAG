"""Bootstrap helpers for the API app."""

from __future__ import annotations

from pathlib import Path

from src.layer8_runtime.bootstrap.startup import BootstrapSequence


def create_bootstrap_sequence(config_dir: Path | None = None) -> BootstrapSequence:
    """Create a bootstrap sequence rooted at the project config directory."""
    resolved_config_dir = config_dir or Path(__file__).resolve().parents[2] / "configs"
    return BootstrapSequence(config_dir=resolved_config_dir)
