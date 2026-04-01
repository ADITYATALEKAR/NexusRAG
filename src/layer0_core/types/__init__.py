"""Shared type aliases."""

from __future__ import annotations

from typing import Any

JSONDict = dict[str, Any]
JSONValue = str | int | float | bool | None | JSONDict | list[Any]

__all__ = ["JSONDict", "JSONValue"]
