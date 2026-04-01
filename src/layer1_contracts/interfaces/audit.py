"""Audit interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from src.layer1_contracts.schemas.security import AuditEvent


class AuditInterface(ABC):
    """Abstract interface for audit logging."""

    @abstractmethod
    async def log(self, event: AuditEvent) -> None:
        """Log an audit event."""

    @abstractmethod
    async def query(
        self,
        event_type: str | None = None,
        request_id: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """Query audit events."""
