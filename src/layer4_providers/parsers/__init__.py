"""Parser provider adapters."""

from src.layer4_providers.parsers.fallback.adapter import FallbackTextParser
from src.layer4_providers.parsers.pymupdf.adapter import PyMuPDFParser
from src.layer4_providers.parsers.registry import build_default_parsers

__all__ = ["FallbackTextParser", "PyMuPDFParser", "build_default_parsers"]
