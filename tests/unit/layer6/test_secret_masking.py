"""Tests for secret masking."""

from src.layer6_security.secrets.masking import SecretMasker


def test_secret_masker_redacts_openai_keys() -> None:
    """OpenAI-style keys should be masked."""
    masker = SecretMasker()
    masked = masker.mask("token=sk-abcdefghijklmnopqrstuvwxyz123456")

    assert "sk-" not in masked
    assert "***REDACTED***" in masked
