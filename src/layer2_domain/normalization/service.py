"""Normalization service."""

from __future__ import annotations

import re

from src.layer1_contracts.schemas.document import DocumentMetadata
from src.layer1_contracts.schemas.normalization import NormalizedDocument, NormalizedSection
from src.layer1_contracts.schemas.parsing import ParseResult
from src.layer2_domain.normalization.list_extractor import ListExtractor
from src.layer2_domain.normalization.section_detector import DetectedHeading, SectionDetector
from src.layer2_domain.normalization.table_extractor import TableExtractor


class NormalizationService:
    """Normalize parser output into canonical documents and sections."""

    CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```")

    def __init__(
        self,
        section_detector: SectionDetector,
        table_extractor: TableExtractor | None = None,
        list_extractor: ListExtractor | None = None,
    ) -> None:
        self.section_detector = section_detector
        self.table_extractor = table_extractor or TableExtractor()
        self.list_extractor = list_extractor or ListExtractor()

    async def normalize(self, parse_result: ParseResult, document_id: str) -> NormalizedDocument:
        """Normalize a parsed document into a canonical representation."""
        headings = self.section_detector.detect(parse_result.raw_text)
        sections = self._build_sections(parse_result.raw_text, headings, parse_result)
        word_count = len(parse_result.raw_text.split())
        char_count = len(parse_result.raw_text)
        tables = self.table_extractor.extract(parse_result)
        lists = self.list_extractor.extract(parse_result.raw_text)
        code_blocks = self._extract_code_blocks(parse_result.raw_text)

        metadata = DocumentMetadata(
            page_count=len(parse_result.pages),
            word_count=word_count,
            char_count=char_count,
            custom=dict(parse_result.metadata),
        )

        return NormalizedDocument(
            id=f"norm-{document_id}",
            original_document_id=document_id,
            content=parse_result.raw_text,
            sections=sections,
            tables=tables,
            code_blocks=code_blocks,
            lists=lists,
            metadata=metadata,
            page_count=len(parse_result.pages),
            word_count=word_count,
            char_count=char_count,
        )

    def _build_sections(
        self,
        text: str,
        headings: list[DetectedHeading],
        parse_result: ParseResult,
    ) -> list[NormalizedSection]:
        """Build normalized sections from detected headings."""
        if not headings:
            return [
                NormalizedSection(
                    id="section-0",
                    level=0,
                    content=text,
                    start_char=0,
                    end_char=len(text),
                    page_numbers=self._page_numbers_for_range(parse_result, 0, len(text)),
                )
            ]

        sections: list[NormalizedSection] = []
        for index, heading in enumerate(headings):
            content_start = heading.end_char
            content_end = headings[index + 1].start_char if index + 1 < len(headings) else len(text)
            content = text[content_start:content_end].strip()
            sections.append(
                NormalizedSection(
                    id=f"section-{index}",
                    title=heading.text,
                    level=heading.level,
                    content=content,
                    start_char=heading.start_char,
                    end_char=content_end,
                    page_numbers=self._page_numbers_for_range(parse_result, heading.start_char, content_end),
                )
            )
        self._link_hierarchy(sections)
        return sections

    def _link_hierarchy(self, sections: list[NormalizedSection]) -> None:
        """Link parent-child relationships using heading levels."""
        stack: list[NormalizedSection] = []
        for section in sections:
            while stack and stack[-1].level >= section.level:
                stack.pop()
            if stack:
                section.parent_id = stack[-1].id
                stack[-1].children_ids.append(section.id)
            stack.append(section)

    def _page_numbers_for_range(
        self,
        parse_result: ParseResult,
        start_char: int,
        end_char: int,
    ) -> list[int]:
        """Map character ranges back to page numbers."""
        page_numbers: list[int] = []
        cursor = 0
        for page in parse_result.pages:
            page_start = cursor
            page_end = cursor + len(page.content)
            if page_end >= start_char and page_start <= end_char:
                page_numbers.append(page.page_number)
            cursor = page_end + 2
        return page_numbers

    def _extract_code_blocks(self, text: str) -> list[dict]:
        """Extract fenced code blocks from text."""
        code_blocks: list[dict] = []
        for index, match in enumerate(self.CODE_BLOCK_PATTERN.finditer(text)):
            code_blocks.append(
                {
                    "id": f"code-{index}",
                    "content": match.group(0),
                    "start_char": match.start(),
                    "end_char": match.end(),
                }
            )
        return code_blocks
