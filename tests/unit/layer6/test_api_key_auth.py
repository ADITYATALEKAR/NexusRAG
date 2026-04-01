"""Unit tests for Phase 8 API key auth."""

from __future__ import annotations

from src.layer6_security.auth.api_key import APIKeyAuth


def test_api_key_auth_validates_registered_keys() -> None:
    """Hashed API key validation should accept known keys and reject others."""
    auth = APIKeyAuth(["alpha-key", "beta-key"])
    assert auth.validate("alpha-key") is True
    assert auth.validate("missing-key") is False
    assert auth.fingerprint("alpha-key")


def test_api_key_generation_has_expected_prefix() -> None:
    """Generated API keys should use the rag_ prefix."""
    generated = APIKeyAuth.generate_key()
    assert generated.startswith("rag_")
