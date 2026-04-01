"""Parsing contracts."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ParsedPage(BaseModel):
    """Parsed content for one page."""

    model_config = ConfigDict(extra="forbid")

    page_number: int = Field(ge=1)
    content: str
    tables: list[dict] = Field(default_factory=list)
    images: list[dict] = Field(default_factory=list)


class ParsedSection(BaseModel):
    """Parsed section metadata."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    level: int = Field(ge=0)
    content: str
    start_page: int | None = None
    end_page: int | None = None
    parent_index: int | None = None
    children_indices: list[int] = Field(default_factory=list)


class ParseResult(BaseModel):
    """Structured parser output."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    raw_text: str
    pages: list[ParsedPage] = Field(default_factory=list)
    sections: list[ParsedSection] = Field(default_factory=list)
    tables: list[dict] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    parser_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    warnings: list[str] = Field(default_factory=list)
    parse_time_ms: int
