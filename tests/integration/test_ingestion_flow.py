"""Integration tests for the ingestion flow."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.layer1_contracts.interfaces.parser import ParserInterface
from src.layer1_contracts.schemas.parsing import ParseResult, ParsedPage
from src.layer2_domain.ingestion.file_guards import FileGuard
from src.layer2_domain.ingestion.service import IngestionService
from src.layer2_domain.normalization.chunk_preparer import ChunkPreparer
from src.layer2_domain.normalization.section_detector import SectionDetector
from src.layer2_domain.normalization.service import NormalizationService
from src.layer2_domain.parsing.registry import ParserRegistry
from src.layer2_domain.parsing.service import ParsingService
from src.layer3_flows.ingestion_flow.flow import IngestionFlow
from src.layer4_providers.parsers.fallback.adapter import FallbackTextParser
from src.layer4_providers.parsers.pymupdf.adapter import PyMuPDFParser


class LowConfidenceTextParser(ParserInterface):
    """Primary parser that forces the fallback path."""

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


def build_flow(registry: ParserRegistry) -> IngestionFlow:
    """Build a fully wired ingestion flow for tests."""
    normalization_service = NormalizationService(section_detector=SectionDetector())
    return IngestionFlow(
        file_guard=FileGuard(),
        parser_registry=registry,
        normalization_service=normalization_service,
        chunk_preparer=ChunkPreparer(),
    )


@pytest.mark.asyncio
async def test_full_pdf_ingestion() -> None:
    """Ingest simple.pdf end-to-end and verify normalized output signals."""
    registry = ParserRegistry()
    registry.register("pymupdf", PyMuPDFParser(), priority=10)
    registry.register("fallback_text", FallbackTextParser(), priority=1)
    flow = build_flow(registry)

    request = IngestionService().create_request("tests/fixtures/golden_corpus/simple.pdf")
    result = await flow.execute(request)

    assert result.status.value == "completed"
    assert result.parser_used == "pymupdf"
    assert result.page_count >= 1
    assert result.chunk_count >= 1


@pytest.mark.asyncio
async def test_fallback_parser_activation() -> None:
    """Force low-confidence parse and verify fallback parser activation."""
    registry = ParserRegistry()
    registry.register("low_confidence", LowConfidenceTextParser(), priority=10)
    registry.register("fallback_text", FallbackTextParser(), priority=1)
    flow = build_flow(registry)

    request = IngestionService().create_request("tests/fixtures/golden_corpus/text_only.txt")
    result = await flow.execute(request)

    assert result.status.value == "completed"
    assert result.parser_used == "fallback_text"


@pytest.mark.asyncio
async def test_markdown_ingestion_via_fallback(tmp_path: Path) -> None:
    """Markdown files should ingest successfully through the text fallback parser."""
    registry = ParserRegistry()
    registry.register("fallback_text", FallbackTextParser(), priority=1)
    flow = build_flow(registry)

    file_path = tmp_path / "guide.md"
    file_path.write_text("# Guide\n\nVectorCore normalizes markdown safely.\n", encoding="utf-8")

    request = IngestionService().create_request(str(file_path))
    result = await flow.execute(request)

    assert result.status.value == "completed"
    assert result.parser_used == "fallback_text"
    assert result.page_count == 1
    assert result.chunk_count >= 1


@pytest.mark.asyncio
async def test_section_preservation() -> None:
    """Verify section boundaries survive normalization."""
    registry = ParserRegistry()
    registry.register("fallback_text", FallbackTextParser(), priority=1)
    parsing_service = ParsingService(parser_registry=registry)
    normalization_service = NormalizationService(section_detector=SectionDetector())

    file_path = Path("tests/fixtures/golden_corpus/text_only.txt")
    parse_result = await parsing_service.parse(str(file_path), document_id="doc-1")
    normalized = await normalization_service.normalize(parse_result, document_id="doc-1")

    assert normalized.sections
    assert any(section.title == "VectorCore Overview" for section in normalized.sections)
    assert all(section.page_numbers == [1] for section in normalized.sections)


@pytest.mark.asyncio
async def test_complex_layout_pdf_ingestion() -> None:
    """Complex-layout PDFs should still ingest end-to-end with page metadata."""
    registry = ParserRegistry()
    registry.register("pymupdf", PyMuPDFParser(), priority=10)
    registry.register("fallback_text", FallbackTextParser(), priority=1)
    flow = build_flow(registry)

    request = IngestionService().create_request("tests/fixtures/golden_corpus/complex_layout.pdf")
    result = await flow.execute(request)

    assert result.status.value == "completed"
    assert result.parser_used == "pymupdf"
    assert result.page_count >= 1
    assert result.chunk_count >= 1


@pytest.mark.asyncio
async def test_table_pdf_normalization_preserves_tables() -> None:
    """Table-bearing PDFs should keep table metadata after normalization."""
    normalization_service = NormalizationService(section_detector=SectionDetector())
    parse_result = await PyMuPDFParser().parse("tests/fixtures/golden_corpus/with_tables.pdf")
    parse_result.document_id = "doc-with-tables"

    normalized = await normalization_service.normalize(parse_result, document_id="doc-with-tables")

    assert parse_result.parser_name == "pymupdf"
    assert normalized.page_count >= 1
    assert normalized.tables
