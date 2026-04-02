"""System bootstrap sequence."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import logging

from src.layer0_core.enums.wiring import ComponentStatus, LinkType
from src.layer1_contracts.schemas.health import ComponentHealth, HealthStatus, SystemHealth
from src.layer2_domain.failover.service import FailoverService
from src.layer2_domain.failover.state_machine import FailoverConfig as DomainFailoverConfig
from src.layer4_providers.llms.registry import build_mock_provider
from src.layer5_wiring.monitoring.health_monitor import HealthMonitor
from src.layer5_wiring.registry.component_registry import ComponentRegistry
from src.layer5_wiring.registry.contract_registry import ContractRegistry
from src.layer5_wiring.registry.dependency_registry import DependencyRegistry
from src.layer5_wiring.registry.provider_registry import ProviderRegistry
from src.layer5_wiring.validation.startup_validator import StartupValidationResult, StartupValidator
from src.layer6_security.audit.event_store import InMemoryAuditEventStore
from src.layer6_security.input.injection_detection import InjectionDetector
from src.layer6_security.input.sanitization import InputSanitizer, SanitizationConfig
from src.layer6_security.input.validation import InputValidator
from src.layer6_security.secrets.masking import SecretMasker
from src.layer8_runtime.config.loader import ConfigLoader
from src.layer8_runtime.config.schemas import (
    AppConfig,
    AppFileConfig,
    FailoverFileConfig,
    InputGuardsConfig,
    SystemMapConfig,
)

logger = logging.getLogger(__name__)


@dataclass
class StartupResult:
    """Bootstrap output."""

    ready: bool
    app_config: AppConfig
    startup_validation: StartupValidationResult
    system_health: SystemHealth
    component_registry: ComponentRegistry
    dependency_registry: DependencyRegistry
    provider_registry: ProviderRegistry
    health_monitor: HealthMonitor
    failover_service: FailoverService
    config_loader: ConfigLoader
    initialization_order: list[str] = field(default_factory=list)


class BootstrapSequence:
    """Load config, validate wiring, initialize components, and mark the system ready."""

    def __init__(self, config_dir: Path) -> None:
        self.config_dir = config_dir

    async def run(self) -> StartupResult:
        """Execute the startup sequence."""
        config_loader = ConfigLoader(config_dir=self.config_dir)
        app_file_config = config_loader.load_validated(
            "app/app.yaml",
            AppFileConfig,
            apply_env_overrides=False,
        )
        failover_file_config = config_loader.load_validated(
            "models/llm-failover.yaml",
            FailoverFileConfig,
            apply_env_overrides=False,
        )
        system_map = config_loader.load_validated(
            "wiring/system-map.yaml",
            SystemMapConfig,
            apply_env_overrides=False,
        )
        input_guards = config_loader.load_validated(
            "security/input-guards.yaml",
            InputGuardsConfig,
            apply_env_overrides=False,
        )
        app_config = app_file_config.flatten()

        component_registry = ComponentRegistry()
        dependency_registry = DependencyRegistry()
        contract_registry = ContractRegistry()
        provider_registry = ProviderRegistry()

        sanitizer = InputSanitizer(
            SanitizationConfig(
                max_length=input_guards.max_query_length,
                strip_html=input_guards.strip_html,
                strip_control_chars=input_guards.strip_control_chars,
                normalize_unicode=input_guards.normalize_unicode,
            )
        )
        input_validator = InputValidator(
            max_query_length=input_guards.max_query_length,
            max_document_size_bytes=input_guards.max_document_size_bytes,
        )
        injection_detector = InjectionDetector()
        secret_masker = SecretMasker()
        audit_store = InMemoryAuditEventStore()
        health_monitor = HealthMonitor(component_registry=component_registry)

        provider_items = sorted(
            [item for item in failover_file_config.failover.provider_chain if item.enabled],
            key=lambda item: item.priority,
        )[: failover_file_config.failover.max_providers]
        for item in provider_items:
            await provider_registry.register(
                build_mock_provider(item.provider_id, vendor=item.vendor, model=item.model)
            )

        domain_failover_config = DomainFailoverConfig(
            max_retries=failover_file_config.failover.retry.max_retries,
            base_delay_seconds=failover_file_config.failover.retry.base_delay_seconds,
            max_delay_seconds=failover_file_config.failover.retry.max_delay_seconds,
            backoff_multiplier=failover_file_config.failover.retry.backoff_multiplier,
            jitter=failover_file_config.failover.retry.jitter,
            cooldown_duration_seconds=failover_file_config.failover.cooldown.default_duration_seconds,
            max_cooldown_duration_seconds=failover_file_config.failover.cooldown.max_duration_seconds,
            consecutive_failures_threshold=(
                failover_file_config.failover.cooldown.consecutive_failures_threshold
            ),
        )
        failover_service = FailoverService(provider_registry.get_all(), config=domain_failover_config)

        known_instances = {
            "config_loader": config_loader,
            "component_registry": component_registry,
            "dependency_registry": dependency_registry,
            "contract_registry": contract_registry,
            "provider_registry": provider_registry,
            "health_monitor": health_monitor,
            "input_sanitizer": sanitizer,
            "input_validator": input_validator,
            "injection_detector": injection_detector,
            "secret_masker": secret_masker,
            "audit_event_store": audit_store,
            "failover_service": failover_service,
        }

        for component in system_map.components:
            component_registry.register(
                component_id=component.id,
                instance=known_instances.get(component.id),
                component_type=component.component_type,
                layer=component.layer,
                required=component.required,
            )

        for dependency in system_map.dependencies:
            dependency_registry.add(
                dependency.from_component,
                dependency.to_component,
                LinkType(dependency.link_type),
            )

        contract_registry.register("app_config", AppConfig)
        contract_registry.register("system_map", SystemMapConfig)
        contract_registry.register("input_guards", InputGuardsConfig)

        strict_mode = app_config.startup.validation_mode == "strict"
        startup_validation = StartupValidator(
            component_registry=component_registry,
            dependency_registry=dependency_registry,
            strict_mode=strict_mode,
        ).validate()

        initialization_order = startup_validation.ordered_components + [
            component.id
            for component in component_registry.all_components()
            if component.id not in startup_validation.ordered_components
        ]

        for component_id in initialization_order:
            component = component_registry.get(component_id)
            if component is None:
                continue
            if component.instance is None:
                component_registry.set_status(component_id, ComponentStatus.FAILED)
                continue
            component_registry.set_status(component_id, ComponentStatus.INITIALIZING)
            component_registry.set_status(component_id, ComponentStatus.READY)
            logger.info(
                "Initialized component",
                extra={"component_id": component_id, "request_id": "startup"},
            )

        for component in component_registry.all_components():
            health_monitor.register_check(
                component_id=component.id,
                check_fn=self._make_component_check(component_registry, component.id),
            )

        system_health = await health_monitor.check_all()
        provider_health = list((await provider_registry.refresh_all_health()).values())
        system_health.providers = provider_health
        ready = component_registry.all_required_ready() and any(
            provider.is_available for provider in provider_health
        )
        return StartupResult(
            ready=ready,
            app_config=app_config,
            startup_validation=startup_validation,
            system_health=system_health,
            component_registry=component_registry,
            dependency_registry=dependency_registry,
            provider_registry=provider_registry,
            health_monitor=health_monitor,
            failover_service=failover_service,
            config_loader=config_loader,
            initialization_order=initialization_order,
        )

    @staticmethod
    def _make_component_check(
        component_registry: ComponentRegistry,
        component_id: str,
    ):
        """Build a simple health check for a registered component."""

        async def check() -> ComponentHealth:
            component = component_registry.get(component_id)
            if component is None:
                return ComponentHealth(
                    component_id=component_id,
                    component_type="unknown",
                    status=HealthStatus.UNHEALTHY,
                    message="Component not registered",
                )
            status = HealthStatus.HEALTHY if component.status == ComponentStatus.READY else HealthStatus.UNHEALTHY
            return ComponentHealth(
                component_id=component.id,
                component_type=component.component_type,
                status=status,
            )

        return check
