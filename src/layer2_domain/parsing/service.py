"""Parsing service."""

from __future__ import annotations

from src.layer0_core.errors.base import ValidationError
from src.layer1_contracts.schemas.parsing import ParseResult
from src.layer2_domain.parsing.fallback_selector import FallbackSelector
from src.layer2_domain.parsing.quality_checker import ParseQualityChecker
from src.layer2_domain.parsing.registry import ParserRegistry


class ParsingService:
    """Parse files using a registry of adapters plus fallback logic."""

    def __init__(
        self,
        parser_registry: ParserRegistry,
        quality_checker: ParseQualityChecker | None = None,
        fallback_selector: FallbackSelector | None = None,
    ) -> None:
        self.parser_registry = parser_registry
        self.quality_checker = quality_checker or ParseQualityChecker()
        self.fallback_selector = fallback_selector or FallbackSelector()

    async def parse(self, file_path: str, document_id: str) -> ParseResult:
        """Parse a file and activate fallback when confidence is too low."""
        parser = self.parser_registry.get_parser(file_path)
        if parser is None:
            raise ValidationError(f"No parser for: {file_path}")

        primary_result = await parser.parse(file_path)
        primary_result.document_id = document_id
        primary_result.confidence = self.quality_checker.assess(primary_result)

        if self.fallback_selector.should_use_fallback(primary_result):
            fallback = self.parser_registry.get_fallback(file_path)
            if fallback is not None and fallback is not parser:
                fallback_result = await fallback.parse(file_path)
                fallback_result.document_id = document_id
                fallback_result.confidence = self.quality_checker.assess(fallback_result)
                return self.fallback_selector.select(primary_result, fallback_result)

        return primary_result
