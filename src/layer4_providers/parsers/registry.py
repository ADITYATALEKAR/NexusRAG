"""Parser adapter registry helpers."""

from __future__ import annotations

from src.layer1_contracts.interfaces.parser import ParserInterface
from src.layer4_providers.parsers.fallback.adapter import FallbackTextParser
from src.layer4_providers.parsers.pymupdf.adapter import PyMuPDFParser


def build_default_parsers() -> dict[str, tuple[ParserInterface, int]]:
    """Build the default parser adapter set for Phase 1."""
    return {
        "pymupdf": (PyMuPDFParser(), 10),
        "fallback_text": (FallbackTextParser(), 1),
    }
