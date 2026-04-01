"""Section boundary detection."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class DetectedHeading:
    """Detected heading metadata."""

    text: str
    level: int
    start_char: int
    end_char: int


class SectionDetector:
    """Detect section boundaries and headings."""

    HEADING_PATTERNS = [
        (re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE), lambda match: (len(match.group(1)), match.group(2))),
        (
            re.compile(r"^(\d+(?:\.\d+)*)\s+(.+)$", re.MULTILINE),
            lambda match: (match.group(1).count(".") + 1, match.group(2)),
        ),
        (
            re.compile(r"^([A-Z][A-Z\s]{4,50})$", re.MULTILINE),
            lambda match: (1, match.group(1).strip()),
        ),
    ]

    def detect(self, text: str) -> list[DetectedHeading]:
        """Detect headings using multiple heuristics."""
        headings: list[DetectedHeading] = []
        for pattern, extractor in self.HEADING_PATTERNS:
            for match in pattern.finditer(text):
                level, title = extractor(match)
                headings.append(
                    DetectedHeading(
                        text=title.strip(),
                        level=level,
                        start_char=match.start(),
                        end_char=match.end(),
                    )
                )
        headings.sort(key=lambda heading: heading.start_char)
        return self._deduplicate(headings)

    def _deduplicate(self, headings: list[DetectedHeading]) -> list[DetectedHeading]:
        """Remove overlapping or duplicate heading detections."""
        if not headings:
            return []
        result = [headings[0]]
        for heading in headings[1:]:
            if heading.start_char >= result[-1].end_char:
                result.append(heading)
        return result
