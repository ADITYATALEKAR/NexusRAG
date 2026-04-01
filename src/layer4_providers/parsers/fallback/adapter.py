"""Fallback text parser."""

from __future__ import annotations

from datetime import datetime, timezone

from src.layer1_contracts.interfaces.parser import ParserInterface
from src.layer1_contracts.schemas.parsing import ParseResult, ParsedPage


class FallbackTextParser(ParserInterface):
    """Simple text extraction for text-like files and last-resort fallback."""

    @property
    def supported_types(self) -> list[str]:
        """Return supported text-like extensions."""
        return [".txt", ".md", ".html", ".csv", ".json"]

    def supports(self, filename: str) -> bool:
        """Return whether the filename is supported."""
        return any(filename.lower().endswith(extension) for extension in self.supported_types)

    async def parse(self, file_path: str) -> ParseResult:
        """Parse a text-like file into a single-page parse result."""
        start = datetime.now(timezone.utc)
        with open(file_path, "r", encoding="utf-8", errors="replace") as file_handle:
            content = file_handle.read()
        elapsed_ms = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
        return ParseResult(
            document_id="",
            raw_text=content,
            pages=[ParsedPage(page_number=1, content=content)],
            metadata={"page_count": 1},
            parser_name="fallback_text",
            confidence=0.7,
            parse_time_ms=elapsed_ms,
        )
