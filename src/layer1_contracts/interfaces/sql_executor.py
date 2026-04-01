"""Abstract interface for bounded structured-query execution."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SQLExecutorInterface(ABC):
    """Execute readonly SQL against an application metadata store."""

    @abstractmethod
    def execute(self, sql: str, parameters: list[Any] | tuple[Any, ...]) -> Any:
        """Execute one readonly query and return a cursor-like object."""

    @abstractmethod
    def ensure_supporting_views(self) -> None:
        """Create any readonly compatibility views required by structured retrieval."""
