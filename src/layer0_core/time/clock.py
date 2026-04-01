"""Clock abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone


class Clock(ABC):
    """Abstract time source."""

    @abstractmethod
    def now(self) -> datetime:
        """Return the current time."""

    @abstractmethod
    def now_ms(self) -> int:
        """Return the current time in epoch milliseconds."""


class SystemClock(Clock):
    """UTC-backed system clock."""

    def now(self) -> datetime:
        """Return the current UTC time."""
        return datetime.now(timezone.utc)

    def now_ms(self) -> int:
        """Return epoch milliseconds."""
        return int(self.now().timestamp() * 1000)


class MockClock(Clock):
    """Controllable clock for testing."""

    def __init__(self, fixed_time: datetime | None = None) -> None:
        self._time = fixed_time or datetime(2024, 1, 1, tzinfo=timezone.utc)

    def now(self) -> datetime:
        """Return the mocked time."""
        return self._time

    def now_ms(self) -> int:
        """Return mocked epoch milliseconds."""
        return int(self._time.timestamp() * 1000)

    def advance(self, seconds: float) -> None:
        """Advance time by a number of seconds."""
        self._time += timedelta(seconds=seconds)

    def set(self, time: datetime) -> None:
        """Set the mocked time."""
        self._time = time
