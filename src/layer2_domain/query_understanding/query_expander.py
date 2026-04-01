"""Query expansion helpers."""

from __future__ import annotations

import re


class QueryExpander:
    """Expand useful query terms without drifting into open-ended rewriting."""

    SYNONYM_MAP: dict[str, list[str]] = {
        "compare": ["contrast"],
        "difference": ["distinction"],
        "count": ["total"],
        "average": ["mean"],
        "error": ["failure"],
        "docs": ["documents"],
    }

    def expand_keywords(self, text: str) -> list[str]:
        """Return normalized keywords with a small synonym expansion set."""
        base_keywords = self._extract_keywords(text)
        expanded: list[str] = []
        seen: set[str] = set()
        for keyword in base_keywords:
            for candidate in [keyword, *self.SYNONYM_MAP.get(keyword, [])]:
                if candidate not in seen:
                    expanded.append(candidate)
                    seen.add(candidate)
        return expanded

    def _extract_keywords(self, text: str) -> list[str]:
        stopwords = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "what",
            "how",
            "why",
            "when",
            "where",
            "who",
            "which",
            "to",
            "for",
            "of",
            "in",
            "on",
            "at",
            "and",
            "or",
            "but",
            "with",
            "this",
            "that",
            "it",
            "be",
            "do",
            "does",
        }
        words = re.findall(r"\b\w+\b", text.lower())
        return [word for word in words if word not in stopwords and len(word) > 2]
