"""Shared helpers for the CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
import typer

CONFIG_DIR = Path.home() / ".rag"
CONFIG_PATH = CONFIG_DIR / "config.yaml"
DEFAULT_CONFIG = {
    "api_url": "http://localhost:8000",
    "api_key": "",
    "timeout": 30.0,
}


def load_config() -> dict:
    """Load CLI config, falling back to defaults."""
    if not CONFIG_PATH.exists():
        return dict(DEFAULT_CONFIG)
    payload = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        return dict(DEFAULT_CONFIG)
    return {**DEFAULT_CONFIG, **payload}


def save_config(config: dict) -> None:
    """Persist CLI config under the user's home directory."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(yaml.safe_dump(config, sort_keys=True), encoding="utf-8")


def get_config(key: str, default=None):
    """Return a single CLI config value."""
    return load_config().get(key, default)


def set_config(key: str, value) -> None:
    """Set and persist one CLI config value."""
    config = load_config()
    config[key] = value
    save_config(config)


def resolve_cli_value(value: Any) -> Any:
    """Unwrap Typer OptionInfo defaults when command functions are called directly."""
    if value.__class__.__module__.startswith("typer.") and hasattr(value, "default"):
        return value.default
    return value


def parse_bool_option(value: bool | str, option_name: str) -> bool:
    """Normalize CLI bool-like option values into booleans."""
    value = resolve_cli_value(value)
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise typer.BadParameter(
        f"{option_name} must be one of: true, false, yes, no, on, off, 1, 0",
    )
