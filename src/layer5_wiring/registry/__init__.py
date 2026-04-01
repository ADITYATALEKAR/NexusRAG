"""Wiring registries."""

from src.layer5_wiring.registry.component_registry import ComponentInfo, ComponentRegistry
from src.layer5_wiring.registry.contract_registry import ContractRegistry
from src.layer5_wiring.registry.dependency_registry import Dependency, DependencyRegistry
from src.layer5_wiring.registry.provider_registry import ProviderRegistry

__all__ = [
    "ComponentInfo",
    "ComponentRegistry",
    "ContractRegistry",
    "Dependency",
    "DependencyRegistry",
    "ProviderRegistry",
]
