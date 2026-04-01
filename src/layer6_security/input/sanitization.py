"""Input sanitization."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass
class SanitizationConfig:
    """Sanitization settings."""

    strip_null_bytes: bool = True
    normalize_unicode: bool = True
    max_length: int | None = None
    strip_html: bool = True
    strip_control_chars: bool = True


class InputSanitizer:
    """Safe text transformations for untrusted input."""

    CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
    HTML_TAG_PATTERN = re.compile(r"<[^>]+>")

    def __init__(self, config: SanitizationConfig | None = None) -> None:
        self.config = config or SanitizationConfig()

    def sanitize(self, text: str) -> tuple[str, list[str]]:
        """Sanitize input text and return modifications performed."""
        modifications: list[str] = []
        result = text

        if self.config.strip_null_bytes and "\x00" in result:
            result = result.replace("\x00", "")
            modifications.append("stripped_null_bytes")

        if self.config.strip_control_chars:
            new_result = self.CONTROL_CHAR_PATTERN.sub("", result)
            if new_result != result:
                result = new_result
                modifications.append("stripped_control_chars")

        if self.config.normalize_unicode:
            new_result = unicodedata.normalize("NFC", result)
            if new_result != result:
                result = new_result
                modifications.append("normalized_unicode")

        if self.config.strip_html:
            new_result = self.HTML_TAG_PATTERN.sub("", result)
            if new_result != result:
                result = new_result
                modifications.append("stripped_html")

        if self.config.max_length and len(result) > self.config.max_length:
            result = result[: self.config.max_length]
            modifications.append(f"truncated_to_{self.config.max_length}")

        return result, modifications
