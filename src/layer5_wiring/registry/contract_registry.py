"""Contract registry."""

from __future__ import annotations

from typing import Any


class ContractRegistry:
    """Registry for schemas and interfaces."""

    def __init__(self) -> None:
        self._contracts: dict[str, Any] = {}

    def register(self, name: str, contract: Any) -> None:
        """Register a contract type."""
        self._contracts[name] = contract

    def get(self, name: str) -> Any | None:
        """Return a contract by name."""
        return self._contracts.get(name)

    def all(self) -> dict[str, Any]:
        """Return all registered contracts."""
        return dict(self._contracts)
