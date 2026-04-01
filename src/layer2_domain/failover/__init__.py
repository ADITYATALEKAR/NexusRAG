"""Failover domain services."""

from src.layer2_domain.failover.error_classifier import ErrorClassifier
from src.layer2_domain.failover.service import FailoverService
from src.layer2_domain.failover.state_machine import (
    CooldownState,
    FailoverConfig,
    FailoverState,
    FailoverStateMachine,
    ProviderAttempt,
)

__all__ = [
    "CooldownState",
    "ErrorClassifier",
    "FailoverConfig",
    "FailoverService",
    "FailoverState",
    "FailoverStateMachine",
    "ProviderAttempt",
]
