"""Tests for normalization services."""

import pytest

from src.layer1_contracts.schemas.parsing import ParseResult, ParsedPage
from src.layer2_domain.normalization.chunk_preparer import ChunkPreparer
from src.layer2_domain.normalization.section_detector import SectionDetector
from src.layer2_domain.normalization.service import NormalizationService


def test_section_detector_finds_markdown_headings() -> None:
    """Markdown headings should be detected."""
    detector = SectionDetector()
    headings = detector.detect("# Title\n\n## Child")

    assert [heading.text for heading in headings] == ["Title", "Child"]


def test_section_detector_finds_numbered_sections() -> None:
    """Numbered headings should be detected."""
    detector = SectionDetector()
    headings = detector.detect("1 Intro\nBody\n\n1.1 Detail\nBody")

    assert [heading.level for heading in headings] == [1, 2]


@pytest.mark.asyncio
async def test_hierarchy_linking() -> None:
    """Normalization should preserve heading hierarchy."""
    service = NormalizationService(section_detector=SectionDetector())
    parse_result = ParseResult(
        document_id="",
        raw_text="# Root\nroot text\n\n## Child\nchild text",
        pages=[ParsedPage(page_number=1, content="# Root\nroot text\n\n## Child\nchild text")],
        parser_name="fallback_text",
        confidence=0.8,
        parse_time_ms=1,
    )

    normalized = await service.normalize(parse_result, document_id="doc-1")

    assert normalized.sections[1].parent_id == normalized.sections[0].id
    assert normalized.sections[0].children_ids == [normalized.sections[1].id]


@pytest.mark.asyncio
async def test_chunk_preparer_split_points() -> None:
    """Large sections should receive suggested split points."""
    preparer = ChunkPreparer(target_size=50, min_size=10)
    service = NormalizationService(section_detector=SectionDetector())
    parse_result = ParseResult(
        document_id="",
        raw_text="# Title\n" + ("Sentence one. Sentence two. " * 20),
        pages=[ParsedPage(page_number=1, content="# Title\n" + ("Sentence one. Sentence two. " * 20))],
        parser_name="fallback_text",
        confidence=0.8,
        parse_time_ms=1,
    )

    normalized = await service.normalize(parse_result, document_id="doc-1")
    precursors = preparer.prepare(normalized)

    assert precursors
    assert precursors[0].suggested_split_points
