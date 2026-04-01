"""Tests for clock abstractions."""

from datetime import datetime, timezone

from src.layer0_core.time.clock import MockClock


def test_mock_clock_advance_changes_time() -> None:
    """Mock clock should support deterministic movement."""
    clock = MockClock(datetime(2024, 1, 1, tzinfo=timezone.utc))
    original = clock.now()

    clock.advance(10)

    assert clock.now() > original
    assert clock.now_ms() == int(clock.now().timestamp() * 1000)
