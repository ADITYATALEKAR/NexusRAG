"""Parser interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict, Field

from src.layer1_contracts.schemas.parsing import ParseResult


class ParsedDocument(BaseModel):
    """Structured parser output."""

    model_config = ConfigDict(extra="forbid")

    content: str
    pages: list[str] = Field(default_factory=list)
    tables: list[dict] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ParserInterface(ABC):
    """Abstract interface for document parsers."""

    @property
    @abstractmethod
    def supported_types(self) -> list[str]:
        """Return supported file extensions."""

    @abstractmethod
    async def parse(self, file_path: str) -> ParseResult:
        """Parse a file path into structured content."""

    @abstractmethod
    def supports(self, filename: str) -> bool:
        """Return whether the parser supports the filename."""
