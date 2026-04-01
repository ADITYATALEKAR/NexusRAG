"""Entity extraction for routed queries."""

from __future__ import annotations

import re

from src.layer1_contracts.schemas.query_understanding import DetectedEntity


class EntityExtractor:
    """Extract lightweight entities from user queries using regex heuristics."""

    PATTERNS: dict[str, str] = {
        "date": (
            r"\b\d{4}[-/]\d{2}[-/]\d{2}\b|"
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b"
        ),
        "money": r"\$[\d,]+(?:\.\d{2})?|\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars?|USD|EUR)\b",
        "percentage": r"\b\d+(?:\.\d+)?%\b",
        "number": r"\b\d{4,}\b",
        "email": r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b",
        "quoted": r'"([^"]+)"',
    }

    def extract(self, text: str) -> list[DetectedEntity]:
        """Return all detected entities from the supplied text."""
        entities: list[DetectedEntity] = []
        occupied: list[tuple[int, int]] = []

        for entity_type, pattern in self.PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start, end = match.start(), match.end()
                occupied.append((start, end))
                entities.append(
                    DetectedEntity(
                        text=match.group(),
                        entity_type=entity_type,
                        start=start,
                        end=end,
                        confidence=0.9,
                    )
                )

        for match in re.finditer(r"\b[A-Z][a-zA-Z]+\b", text):
            start, end = match.start(), match.end()
            if any(start >= left and end <= right for left, right in occupied):
                continue
            entities.append(
                DetectedEntity(
                    text=match.group(),
                    entity_type="proper_noun",
                    start=start,
                    end=end,
                    confidence=0.6,
                )
            )

        entities.sort(key=lambda entity: (entity.start, entity.end))
        return entities
