"""PyMuPDF parser adapter."""

from __future__ import annotations

from datetime import datetime, timezone

import fitz

from src.layer1_contracts.interfaces.parser import ParserInterface
from src.layer1_contracts.schemas.parsing import ParseResult, ParsedPage


class PyMuPDFParser(ParserInterface):
    """Primary PDF parser backed by PyMuPDF."""

    @property
    def supported_types(self) -> list[str]:
        """Return supported file extensions."""
        return [".pdf"]

    def supports(self, filename: str) -> bool:
        """Return whether the filename is a PDF."""
        return filename.lower().endswith(".pdf")

    async def parse(self, file_path: str) -> ParseResult:
        """Parse a PDF into pages, text, and table metadata."""
        start = datetime.now(timezone.utc)
        document = fitz.open(file_path)

        pages: list[ParsedPage] = []
        all_text: list[str] = []
        tables: list[dict] = []

        try:
            for page_num, page in enumerate(document, 1):
                text = page.get_text("text")
                all_text.append(text)

                page_tables: list[dict] = []
                try:
                    found_tables = page.find_tables()
                    for table_index, table in enumerate(found_tables.tables if found_tables else []):
                        table_payload = {
                            "id": f"table-{page_num}-{table_index}",
                            "page": page_num,
                            "data": table.extract(),
                            "bbox": list(table.bbox),
                        }
                        tables.append(table_payload)
                        page_tables.append(table_payload)
                except Exception:  # noqa: BLE001
                    page_tables = []

                pages.append(
                    ParsedPage(
                        page_number=page_num,
                        content=text,
                        tables=page_tables,
                    )
                )
        finally:
            page_count = document.page_count
            document.close()

        total_chars = sum(len(page.content) for page in pages)
        confidence = min(1.0, total_chars / (max(page_count, 1) * 500)) if page_count > 0 else 0.5
        elapsed_ms = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
        return ParseResult(
            document_id="",
            raw_text="\n\n".join(all_text),
            pages=pages,
            tables=tables,
            metadata={"page_count": page_count},
            parser_name="pymupdf",
            confidence=confidence,
            parse_time_ms=elapsed_ms,
        )
