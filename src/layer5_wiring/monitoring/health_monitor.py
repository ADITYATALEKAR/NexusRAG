"""Periodic health monitoring."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timezone

from src.layer1_contracts.schemas.health import ComponentHealth, HealthStatus, SystemHealth
from src.layer5_wiring.registry.component_registry import ComponentRegistry

HealthCheckFn = Callable[[], Awaitable[ComponentHealth]]


@dataclass
class HealthCheckRegistration:
    """One registered health check."""

    component_id: str
    check_fn: HealthCheckFn
    interval_seconds: int = 30
    timeout_seconds: int = 10
    last_check: datetime | None = None
    last_result: ComponentHealth | None = None


class HealthMonitor:
    """Monitors component health with periodic checks."""

    def __init__(self, component_registry: ComponentRegistry) -> None:
        self.component_registry = component_registry
        self._health_checks: dict[str, HealthCheckRegistration] = {}
        self._running = False
        self._task: asyncio.Task | None = None

    def register_check(
        self,
        component_id: str,
        check_fn: HealthCheckFn,
        interval_seconds: int = 30,
        timeout_seconds: int = 10,
    ) -> None:
        """Register a component health check."""
        self._health_checks[component_id] = HealthCheckRegistration(
            component_id=component_id,
            check_fn=check_fn,
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds,
        )

    async def check_component(self, component_id: str) -> ComponentHealth:
        """Run a health check for one component."""
        registration = self._health_checks.get(component_id)
        component = self.component_registry.get(component_id)
        component_type = component.component_type if component else "unknown"

        if registration is None:
            return ComponentHealth(
                component_id=component_id,
                component_type=component_type,
                status=HealthStatus.UNKNOWN,
                message="No health check registered",
            )

        try:
            health = await asyncio.wait_for(
                registration.check_fn(),
                timeout=registration.timeout_seconds,
            )
        except asyncio.TimeoutError:
            health = ComponentHealth(
                component_id=component_id,
                component_type=component_type,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {registration.timeout_seconds}s",
            )
        except Exception as error:  # noqa: BLE001
            health = ComponentHealth(
                component_id=component_id,
                component_type=component_type,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {error}",
            )

        registration.last_check = datetime.now(timezone.utc)
        registration.last_result = health
        return health

    async def check_all(self) -> SystemHealth:
        """Run all registered health checks."""
        components = [await self.check_component(component_id) for component_id in self._health_checks]
        healthy_count = sum(1 for component in components if component.status == HealthStatus.HEALTHY)
        degraded_count = sum(1 for component in components if component.status == HealthStatus.DEGRADED)
        unhealthy_count = sum(1 for component in components if component.status == HealthStatus.UNHEALTHY)

        if unhealthy_count > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            overall_status = HealthStatus.DEGRADED
        elif components:
            overall_status = HealthStatus.HEALTHY
        else:
            overall_status = HealthStatus.UNKNOWN

        return SystemHealth(
            status=overall_status,
            components=components,
            total_components=len(components),
            healthy_components=healthy_count,
            degraded_components=degraded_count,
            unhealthy_components=unhealthy_count,
        )

    async def start_monitoring(self) -> None:
        """Start the background monitoring loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self) -> None:
        """Stop the background monitoring loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _monitoring_loop(self) -> None:
        """Periodic background health loop."""
        while self._running:
            try:
                await self.check_all()
            except Exception:  # noqa: BLE001
                pass
            await asyncio.sleep(10)
