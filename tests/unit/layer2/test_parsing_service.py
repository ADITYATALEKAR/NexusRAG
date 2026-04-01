"""Tests for parsing services."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.layer1_contracts.interfaces.parser import ParserInterface
from src.layer1_contracts.schemas.parsing import ParseResult, ParsedPage
from src.layer2_domain.parsing.registry import ParserRegistry
from src.layer2_domain.parsing.service import ParsingService
from src.layer4_providers.parsers.fallback.adapter import FallbackTextParser
from src.layer4_providers.parsers.pymupdf.adapter import PyMuPDFParser


class LowConfidenceTextParser(ParserInterface):
    """Primary parser that intentionally returns a weak result."""

    @property
    def supported_types(self) -> list[str]:
        return [".txt"]

    def supports(self, filename: str) -> bool:
        return filename.endswith(".txt")

    async def parse(self, file_path: str) -> ParseResult:
        return ParseResult(
            document_id="",
            raw_text="x",
            pages=[ParsedPage(page_number=1, content="x")],
            parser_name="low_confidence",
            confidence=0.1,
            parse_time_ms=1,
        )


def test_parser_registry_selects_correct_parser() -> None:
    """Registry should select the highest-priority parser."""
    registry = ParserRegistry()
    registry.register("fallback_text", FallbackTextParser(), priority=1)
    registry.register("pymupdf", PyMuPDFParser(), priority=10)

    parser = registry.get_parser("sample.pdf")

    assert parser is not None
    assert isinstance(parser, PyMuPDFParser)


@pytest.mark.asyncio
async def test_fallback_triggers_on_low_confidence() -> None:
    """Low-confidence primary results should trigger the fallback parser."""
    registry = ParserRegistry()
    registry.register("low_confidence", LowConfidenceTextParser(), priority=10)
    registry.register("fallback_text", FallbackTextParser(), priority=1)
    service = ParsingService(parser_registry=registry)

    file_path = Path("tests/fixtures/golden_corpus/text_only.txt")
    result = await service.parse(str(file_path), document_id="doc-1")

    assert result.parser_name == "fallback_text"
    assert result.confidence >= 0.3
