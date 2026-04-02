"""YAML configuration loading with env overrides."""

from __future__ import annotations

from pathlib import Path
import os
from typing import Any, TypeVar

from pydantic import BaseModel
import yaml

from src.layer0_core.errors.base import ConfigurationError, ErrorContext

T = TypeVar("T", bound=BaseModel)


class ConfigLoader:
    """Load YAML config and apply environment overrides."""

    ENV_PREFIX = "RAG"
    ENV_SEPARATOR = "__"

    def __init__(self, config_dir: Path) -> None:
        self.config_dir = config_dir

    def load_yaml(self, relative_path: str, *, apply_env_overrides: bool = True) -> dict[str, Any]:
        """Load YAML from disk and apply env overrides."""
        path = self.config_dir / relative_path
        if not path.exists():
            raise ConfigurationError(
                f"Config file not found: {path}",
                context=ErrorContext(
                    component="config_loader",
                    operation="load_yaml",
                    metadata={"path": str(path)},
                ),
            )
        try:
            loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as error:
            raise ConfigurationError(
                f"Invalid YAML in {path}: {error}",
                context=ErrorContext(
                    component="config_loader",
                    operation="load_yaml",
                    metadata={"path": str(path)},
                ),
                cause=error,
            ) from error
        if not isinstance(loaded, dict):
            raise ConfigurationError(
                f"Config file must contain a mapping: {path}",
                context=ErrorContext(
                    component="config_loader",
                    operation="load_yaml",
                    metadata={"path": str(path)},
                ),
            )
        if apply_env_overrides:
            self._apply_env_overrides(loaded)
        return loaded

    def load_validated(
        self,
        relative_path: str,
        schema: type[T],
        root_key: str | None = None,
        *,
        apply_env_overrides: bool = True,
    ) -> T:
        """Load config and validate it against a Pydantic model."""
        data = self.load_yaml(relative_path, apply_env_overrides=apply_env_overrides)
        if root_key is not None:
            if root_key not in data:
                raise ConfigurationError(
                    f"Missing root key '{root_key}' in {relative_path}",
                    context=ErrorContext(
                        component="config_loader",
                        operation="load_validated",
                        metadata={"path": relative_path, "root_key": root_key},
                    ),
                )
            selected = data[root_key]
            if not isinstance(selected, dict):
                raise ConfigurationError(
                    f"Root key '{root_key}' must contain a mapping",
                    context=ErrorContext(
                        component="config_loader",
                        operation="load_validated",
                        metadata={"path": relative_path, "root_key": root_key},
                    ),
                )
            data = selected
        try:
            return schema.model_validate(data)
        except Exception as error:  # noqa: BLE001
            raise ConfigurationError(
                f"Config validation failed for {relative_path}: {error}",
                context=ErrorContext(
                    component="config_loader",
                    operation="load_validated",
                    metadata={"path": relative_path, "schema": schema.__name__},
                ),
                cause=error,
            ) from error

    def _apply_env_overrides(self, data: dict[str, Any]) -> None:
        """Apply matching environment variables to the nested config mapping."""
        prefix = f"{self.ENV_PREFIX}{self.ENV_SEPARATOR}"
        for key, raw_value in os.environ.items():
            if not key.startswith(prefix):
                continue
            path = key[len(prefix) :].split(self.ENV_SEPARATOR)
            self._set_nested(data, [segment.lower() for segment in path], self._parse_env_value(raw_value))

    def _set_nested(self, data: dict[str, Any], path: list[str], value: Any) -> None:
        """Set a nested value in a mapping, creating intermediate dictionaries."""
        cursor = data
        for key in path[:-1]:
            next_value = cursor.get(key)
            if not isinstance(next_value, dict):
                next_value = {}
                cursor[key] = next_value
            cursor = next_value
        cursor[path[-1]] = value

    @staticmethod
    def _parse_env_value(raw_value: str) -> Any:
        """Parse environment variable values using YAML semantics."""
        try:
            return yaml.safe_load(raw_value)
        except yaml.YAMLError:
            return raw_value
