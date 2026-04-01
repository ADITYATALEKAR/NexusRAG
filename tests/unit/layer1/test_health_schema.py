"""Tests for health schemas."""

from src.layer1_contracts.schemas.health import HealthStatus, SystemHealth


def test_system_health_accepts_degraded_counts() -> None:
    """System health should carry aggregate counts."""
    system_health = SystemHealth(
        status=HealthStatus.DEGRADED,
        total_components=3,
        healthy_components=2,
        degraded_components=1,
        unhealthy_components=0,
    )

    assert system_health.status == HealthStatus.DEGRADED
