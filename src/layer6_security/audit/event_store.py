"""In-memory audit event store."""

from __future__ import annotations

from datetime import datetime

from src.layer1_contracts.interfaces.audit import AuditInterface
from src.layer1_contracts.schemas.security import AuditEvent


class InMemoryAuditEventStore(AuditInterface):
    """Simple in-memory audit store for Phase 0."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    async def log(self, event: AuditEvent) -> None:
        """Store an audit event."""
        self._events.append(event)

    async def query(
        self,
        event_type: str | None = None,
        request_id: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """Query stored events."""
        events = self._events
        if event_type is not None:
            events = [event for event in events if event.event_type == event_type]
        if request_id is not None:
            events = [event for event in events if event.request_id == request_id]
        if start_time is not None:
            events = [event for event in events if event.timestamp >= start_time]
        if end_time is not None:
            events = [event for event in events if event.timestamp <= end_time]
        return events[:limit]
