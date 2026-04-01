"""Integration tests for config loading."""

from pathlib import Path
import shutil

import pytest

from src.layer0_core.errors.base import ConfigurationError
from src.layer8_runtime.config.loader import ConfigLoader
from src.layer8_runtime.config.schemas import AppFileConfig


def test_config_loader_applies_environment_overrides(monkeypatch) -> None:
    """Environment variables should override YAML values."""
    monkeypatch.setenv("RAG__SERVER__PORT", "9000")
    loader = ConfigLoader(config_dir=Path("configs"))

    config = loader.load_validated("app/app.yaml", AppFileConfig)

    assert config.server.port == 9000


def test_config_loader_fails_fast_on_invalid_config(tmp_path: Path) -> None:
    """Invalid config should raise a configuration error."""
    source = Path("configs")
    destination = tmp_path / "configs"
    shutil.copytree(source, destination)
    (destination / "app" / "app.yaml").write_text(
        """
app:
  name: "rag-system"
  version: "0.1.0"
  environment: "development"
  debug: false

server:
  host: "0.0.0.0"
  port: 99999
  workers: 1
  timeout_seconds: 60

startup:
  validation_mode: "strict"
  startup_timeout_seconds: 30
""".strip(),
        encoding="utf-8",
    )
    loader = ConfigLoader(config_dir=destination)

    with pytest.raises(ConfigurationError):
        loader.load_validated("app/app.yaml", AppFileConfig)
