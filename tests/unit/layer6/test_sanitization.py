"""Tests for input sanitization."""

from src.layer6_security.input.sanitization import InputSanitizer, SanitizationConfig


def test_sanitizer_strips_html_control_chars_and_null_bytes() -> None:
    """Sanitizer should apply safe baseline transformations."""
    sanitizer = InputSanitizer(SanitizationConfig(max_length=20))

    sanitized, modifications = sanitizer.sanitize("<b>he\x00llo</b>\x07")

    assert sanitized == "hello"
    assert "stripped_null_bytes" in modifications
    assert "stripped_control_chars" in modifications
    assert "stripped_html" in modifications
