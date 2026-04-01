"""Pydantic models for configuration files."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ServerConfig(BaseModel):
    """HTTP server settings."""

    model_config = ConfigDict(extra="forbid")

    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    workers: int = Field(default=1, ge=1)
    timeout_seconds: int = Field(default=60, ge=1)


class StartupConfig(BaseModel):
    """Startup validation settings."""

    model_config = ConfigDict(extra="forbid")

    validation_mode: str = "strict"
    startup_timeout_seconds: int = 30


class ApplicationSectionConfig(BaseModel):
    """Application identity settings."""

    model_config = ConfigDict(extra="forbid")

    name: str = "rag-system"
    version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False


class AppConfig(BaseModel):
    """Flattened application config used at runtime."""

    model_config = ConfigDict(extra="forbid")

    name: str = "rag-system"
    version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    server: ServerConfig = Field(default_factory=ServerConfig)
    startup: StartupConfig = Field(default_factory=StartupConfig)


class AppFileConfig(BaseModel):
    """Application config file shape."""

    model_config = ConfigDict(extra="forbid")

    app: ApplicationSectionConfig = Field(default_factory=ApplicationSectionConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    startup: StartupConfig = Field(default_factory=StartupConfig)

    def flatten(self) -> AppConfig:
        """Convert file config into runtime config."""
        return AppConfig(
            name=self.app.name,
            version=self.app.version,
            environment=self.app.environment,
            debug=self.app.debug,
            server=self.server,
            startup=self.startup,
        )


class ProviderChainItem(BaseModel):
    """One provider in the failover chain."""

    model_config = ConfigDict(extra="forbid")

    provider_id: str
    vendor: str
    model: str
    priority: int = Field(ge=1)
    enabled: bool = True


class RetryConfig(BaseModel):
    """Retry settings."""

    model_config = ConfigDict(extra="forbid")

    max_retries: int = Field(default=3, ge=0)
    base_delay_seconds: float = Field(default=1.0, ge=0.0)
    max_delay_seconds: float = Field(default=30.0, ge=0.0)
    backoff_multiplier: float = Field(default=2.0, ge=1.0)
    jitter: bool = True


class CooldownConfig(BaseModel):
    """Cooldown settings."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    default_duration_seconds: int = Field(default=60, ge=1)
    max_duration_seconds: int = Field(default=300, ge=1)
    consecutive_failures_threshold: int = Field(default=3, ge=1)


class FailoverConfig(BaseModel):
    """Failover config."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    max_providers: int = Field(default=5, ge=1)
    provider_chain: list[ProviderChainItem] = Field(default_factory=list)
    retry: RetryConfig = Field(default_factory=RetryConfig)
    cooldown: CooldownConfig = Field(default_factory=CooldownConfig)


class FailoverFileConfig(BaseModel):
    """Failover config file shape."""

    model_config = ConfigDict(extra="forbid")

    failover: FailoverConfig


class SystemComponentConfig(BaseModel):
    """Declared runtime component."""

    model_config = ConfigDict(extra="forbid")

    id: str
    component_type: str
    layer: str
    required: bool = False


class SystemDependencyConfig(BaseModel):
    """Declared dependency edge."""

    model_config = ConfigDict(extra="forbid")

    from_component: str
    to_component: str
    link_type: str


class SystemMapConfig(BaseModel):
    """System wiring config."""

    model_config = ConfigDict(extra="forbid")

    components: list[SystemComponentConfig] = Field(default_factory=list)
    dependencies: list[SystemDependencyConfig] = Field(default_factory=list)


class InputGuardsConfig(BaseModel):
    """Security guard config."""

    model_config = ConfigDict(extra="forbid")

    max_query_length: int = Field(default=10000, ge=1)
    max_document_size_bytes: int = Field(default=52428800, ge=1)
    strip_html: bool = True
    strip_control_chars: bool = True
    normalize_unicode: bool = True
