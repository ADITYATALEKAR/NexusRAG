"""Parser registry."""

from __future__ import annotations

from pathlib import Path

from src.layer1_contracts.interfaces.parser import ParserInterface


class ParserRegistry:
    """Registry of parser adapters keyed by supported extensions."""

    def __init__(self) -> None:
        self._parsers: dict[str, ParserInterface] = {}
        self._extension_map: dict[str, list[tuple[str, int]]] = {}

    def register(self, name: str, parser: ParserInterface, priority: int = 0) -> None:
        """Register a parser with a priority for its supported extensions."""
        self._parsers[name] = parser
        for extension in parser.supported_types:
            self._extension_map.setdefault(extension, []).append((name, priority))
            self._extension_map[extension].sort(key=lambda item: item[1], reverse=True)

    def get_parser(self, filename: str) -> ParserInterface | None:
        """Return the highest-priority parser for a file."""
        extension = Path(filename).suffix.lower()
        if extension in self._extension_map and self._extension_map[extension]:
            name = self._extension_map[extension][0][0]
            return self._parsers.get(name)
        return None

    def get_fallback(self, filename: str) -> ParserInterface | None:
        """Return the second-choice parser or the generic text fallback."""
        extension = Path(filename).suffix.lower()
        if extension in self._extension_map and len(self._extension_map[extension]) > 1:
            name = self._extension_map[extension][1][0]
            return self._parsers.get(name)
        return self._parsers.get("fallback_text")
