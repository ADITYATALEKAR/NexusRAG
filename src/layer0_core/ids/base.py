"""Typed identifiers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass(frozen=True, slots=True)
class BaseId:
    """Base class for all typed identifiers."""

    value: str

    def __post_init__(self) -> None:
        """Validate the identifier value."""
        if not self.value or not isinstance(self.value, str):
            raise ValueError(f"ID must be non-empty string, got: {self.value!r}")

    def __str__(self) -> str:
        """Return the raw string form."""
        return self.value

    def __hash__(self) -> int:
        """Hash by type and value to keep ID spaces distinct."""
        return hash((self.__class__.__name__, self.value))

    @classmethod
    def generate(cls) -> "BaseId":
        """Generate a sortable unique ID."""
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return cls(value=f"{ts}-{uuid.uuid4().hex[:12]}")


class DocumentId(BaseId):
    """Typed document identifier."""


class ChunkId(BaseId):
    """Typed chunk identifier."""


class QueryId(BaseId):
    """Typed query identifier."""


class RequestId(BaseId):
    """Typed request identifier."""


class ProviderId(BaseId):
    """Typed provider identifier."""


class ComponentId(BaseId):
    """Typed component identifier."""


class SessionId(BaseId):
    """Typed session identifier."""


class AuditEventId(BaseId):
    """Typed audit event identifier."""
