"""Application lifespan and deployment runtime configuration."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
import os
import signal
from typing import Any

from fastapi import FastAPI

from apps.api.bootstrap import create_bootstrap_sequence
from src.layer0_core.errors.base import ConfigurationError
from src.layer5_wiring.observability.logging import logger
from src.layer6_security.auth.api_key import APIKeyAuth
from src.layer6_security.rate_limiting.backends import MemoryBackend, RedisBackend
from src.layer6_security.rate_limiting.limiter import RateLimiter
from src.layer8_runtime.config.loader import ConfigLoader
from src.layer8_runtime.config.schemas import AppFileConfig


@dataclass(frozen=True)
class SecurityRuntimeConfig:
    """Resolved authentication and CORS settings for the app."""

    api_key_required: bool = False
    api_keys: list[str] = field(default_factory=list)
    rate_limit_enabled: bool = False
    cors_origins: list[str] = field(default_factory=lambda: ["*"])
    cors_allow_credentials: bool = False
    public_demo_mode: bool = False


@dataclass(frozen=True)
class RateLimitRuntimeConfig:
    """Resolved request throttling settings for the app."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10
    backend: str = "memory"


@dataclass(frozen=True)
class DeploymentRuntimeConfig:
    """Environment-specific runtime settings resolved from config and env."""

    environment: str
    debug: bool
    server_host: str
    server_port: int
    server_workers: int
    timeout_keep_alive: int
    log_level: str
    redis_url: str | None
    security: SecurityRuntimeConfig
    rate_limits: RateLimitRuntimeConfig


class ShutdownCoordinator:
    """Track in-flight requests so shutdown can wait for them to finish."""

    def __init__(self) -> None:
        self._active_requests = 0
        self._lock = asyncio.Lock()
        self._idle_event = asyncio.Event()
        self._idle_event.set()
        self._shutdown_started = False

    @property
    def active_requests(self) -> int:
        """Return the current number of in-flight requests."""
        return self._active_requests

    @property
    def shutdown_started(self) -> bool:
        """Return whether shutdown draining has started."""
        return self._shutdown_started

    async def request_started(self) -> None:
        """Register the start of an in-flight request."""
        async with self._lock:
            self._active_requests += 1
            self._idle_event.clear()

    async def request_finished(self) -> None:
        """Register the completion of an in-flight request."""
        async with self._lock:
            self._active_requests = max(0, self._active_requests - 1)
            if self._active_requests == 0:
                self._idle_event.set()

    async def start_shutdown(self) -> None:
        """Mark shutdown as started and allow idle waiting to begin."""
        async with self._lock:
            self._shutdown_started = True
            if self._active_requests == 0:
                self._idle_event.set()

    async def wait_for_idle(self, timeout_seconds: float) -> bool:
        """Wait for all in-flight requests to complete before timing out."""
        try:
            await asyncio.wait_for(self._idle_event.wait(), timeout=timeout_seconds)
        except asyncio.TimeoutError:
            return False
        return True


def load_runtime_config(config_dir: Path) -> DeploymentRuntimeConfig:
    """Resolve deployment runtime settings from YAML and environment variables."""
    loader = ConfigLoader(config_dir=config_dir)
    app_file = loader.load_validated("app/app.yaml", AppFileConfig, apply_env_overrides=False)
    default_runtime = app_file.flatten()

    environment = os.getenv("RAG__ENV", default_runtime.environment).strip().lower() or "development"
    deployment_raw = loader.load_yaml(f"deployment/{environment}.yaml")
    server_raw = deployment_raw.get("server", {})
    security_raw = deployment_raw.get("security", {})
    rate_limit_raw = deployment_raw.get("rate_limits", {})
    logging_raw = deployment_raw.get("logging", {})
    tier_config = loader.load_yaml("security/rate_limits.yaml")
    tier_name = str(os.getenv("RAG__SECURITY__RATE_LIMIT_TIER", "default")).strip().lower()
    tier_limits = (
        tier_config.get("tiers", {}).get(tier_name)
        if tier_name != "default"
        else tier_config.get("default", {})
    ) or {}

    api_keys = _split_env_list(os.getenv("RAG__SECURITY__API_KEYS")) or []
    cors_origins = _split_env_list(os.getenv("RAG__SECURITY__CORS_ORIGINS")) or list(
        security_raw.get("cors_origins", ["*"])
    )
    public_demo_mode = _get_bool_env(
        "NEXUSRAG_PUBLIC_DEMO_MODE",
        _get_bool_env("RAG__SECURITY__PUBLIC_DEMO_MODE", False),
    )
    security = SecurityRuntimeConfig(
        api_key_required=(
            False
            if public_demo_mode
            else _get_bool_env(
                "RAG__SECURITY__API_KEY_REQUIRED",
                bool(security_raw.get("api_key_required", False)),
            )
        ),
        api_keys=api_keys,
        rate_limit_enabled=_get_bool_env(
            "RAG__SECURITY__RATE_LIMIT_ENABLED",
            bool(security_raw.get("rate_limit_enabled", False)),
        ),
        cors_origins=cors_origins or ["*"],
        cors_allow_credentials=_get_bool_env(
            "RAG__SECURITY__CORS_ALLOW_CREDENTIALS",
            bool(security_raw.get("cors_allow_credentials", False)),
        ),
        public_demo_mode=public_demo_mode,
    )
    if security.api_key_required and not security.api_keys:
        raise ConfigurationError(
            "API key authentication is enabled but no API keys were configured",
        )

    return DeploymentRuntimeConfig(
        environment=environment,
        debug=_get_bool_env("RAG__DEBUG", default_runtime.debug),
        server_host=str(os.getenv("RAG__SERVER__HOST", server_raw.get("host", default_runtime.server.host))),
        server_port=int(os.getenv("RAG__SERVER__PORT", server_raw.get("port", default_runtime.server.port))),
        server_workers=int(
            os.getenv("RAG__SERVER__WORKERS", server_raw.get("workers", default_runtime.server.workers))
        ),
        timeout_keep_alive=int(server_raw.get("timeout_keep_alive", default_runtime.server.timeout_seconds)),
        log_level=str(os.getenv("RAG__LOG_LEVEL", logging_raw.get("level", "info"))),
        redis_url=os.getenv("REDIS_URL"),
        security=security,
        rate_limits=RateLimitRuntimeConfig(
            requests_per_minute=int(
                tier_limits.get("requests_per_minute", rate_limit_raw.get("requests_per_minute", 60))
            ),
            requests_per_hour=int(
                tier_limits.get("requests_per_hour", rate_limit_raw.get("requests_per_hour", 1000))
            ),
            burst_size=int(rate_limit_raw.get("burst_size", 10)),
            backend="redis" if os.getenv("REDIS_URL") else "memory",
        ),
    )


def build_lifespan(config_dir: Path):
    """Build an app lifespan handler rooted at the provided config directory."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        runtime_config = load_runtime_config(config_dir)
        bootstrap_sequence = create_bootstrap_sequence(config_dir=config_dir)
        app.state.bootstrap_sequence = bootstrap_sequence
        app.state.runtime_config = runtime_config
        app.state.rate_limit_enabled = runtime_config.security.rate_limit_enabled
        app.state.shutdown_coordinator = ShutdownCoordinator()
        logger.info(
            "api_starting",
            component="api",
            operation="startup",
            environment=runtime_config.environment,
        )

        startup_result = await bootstrap_sequence.run()
        app.state.startup_result = startup_result
        await startup_result.health_monitor.start_monitoring()

        app.state.api_key_auth = APIKeyAuth(runtime_config.security.api_keys)
        backend = _build_rate_limit_backend(runtime_config)
        app.state.rate_limit_backend = backend
        app.state.rate_limiter = RateLimiter(
            backend=backend,
            requests_per_minute=runtime_config.rate_limits.requests_per_minute,
            requests_per_hour=runtime_config.rate_limits.requests_per_hour,
            burst_size=runtime_config.rate_limits.burst_size,
        )

        shutdown_event = asyncio.Event()
        previous_handlers: dict[signal.Signals, object] = {}

        def _handle_shutdown(signum, _frame) -> None:
            try:
                signame = signal.Signals(signum).name
            except ValueError:
                signame = str(signum)
            logger.info("shutdown_signal_received", component="api", operation="shutdown", signal=signame)
            shutdown_event.set()

        for handled_signal in (signal.SIGTERM, signal.SIGINT):
            try:
                previous_handlers[handled_signal] = signal.getsignal(handled_signal)
                signal.signal(handled_signal, _handle_shutdown)
            except (ValueError, AttributeError):
                continue

        logger.info(
            "api_started",
            component="api",
            operation="startup",
            request_id="startup",
            ready=startup_result.ready,
        )
        try:
            yield
        finally:
            logger.info("api_shutting_down", component="api", operation="shutdown")
            shutdown_coordinator = getattr(app.state, "shutdown_coordinator", None)
            if shutdown_coordinator is not None:
                await shutdown_coordinator.start_shutdown()
                drain_timeout = 0.1 if shutdown_event.is_set() else float(runtime_config.timeout_keep_alive)
                drained = await shutdown_coordinator.wait_for_idle(timeout_seconds=max(0.1, drain_timeout))
                logger.info(
                    "api_shutdown_drain_complete",
                    component="api",
                    operation="shutdown",
                    drained=drained,
                    active_requests=shutdown_coordinator.active_requests,
                )
            await startup_result.health_monitor.stop_monitoring()
            await _cleanup_registered_components(startup_result.component_registry.all_components())
            rate_limit_backend = getattr(app.state, "rate_limit_backend", None)
            if rate_limit_backend is not None:
                await rate_limit_backend.close()
            for handled_signal, previous_handler in previous_handlers.items():
                try:
                    signal.signal(handled_signal, previous_handler)
                except (ValueError, AttributeError):
                    continue
            logger.info("api_shutdown_complete", component="api", operation="shutdown")

    return lifespan


def _split_env_list(value: str | None) -> list[str]:
    """Split comma-delimited environment variables into a list."""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _get_bool_env(name: str, default: bool) -> bool:
    """Parse a boolean environment variable with a fallback."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _build_rate_limit_backend(runtime_config: DeploymentRuntimeConfig):
    """Create the configured rate limit backend."""
    if runtime_config.security.rate_limit_enabled and runtime_config.redis_url:
        try:
            return RedisBackend(runtime_config.redis_url)
        except Exception as error:  # noqa: BLE001
            logger.warning(
                "redis_rate_limit_backend_unavailable",
                component="api",
                operation="startup",
                error=str(error),
            )
    return MemoryBackend()


async def _cleanup_registered_components(components: list[Any]) -> None:
    """Close registered component instances that expose cleanup methods."""
    for component in components:
        instance = getattr(component, "instance", None)
        if instance is None:
            continue
        if hasattr(instance, "aclose") and callable(instance.aclose):
            await instance.aclose()
            continue
        if hasattr(instance, "close") and callable(instance.close):
            maybe_awaitable = instance.close()
            if asyncio.iscoroutine(maybe_awaitable):
                await maybe_awaitable
