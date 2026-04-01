"""List normalization helpers."""

from __future__ import annotations

import re


class ListExtractor:
    """Detect bullet and numbered list blocks in text."""

    LIST_BLOCK_PATTERN = re.compile(
        r"((?:^[ \t]*(?:[-*+]|\d+\.)\s+.+(?:\n|$))+)",
        re.MULTILINE,
    )

    def extract(self, text: str) -> list[dict]:
        """Extract list-like blocks from normalized text."""
        lists: list[dict] = []
        for index, match in enumerate(self.LIST_BLOCK_PATTERN.finditer(text)):
            items = [
                line.strip()
                for line in match.group(1).splitlines()
                if line.strip()
            ]
            lists.append(
                {
                    "id": f"list-{index}",
                    "items": items,
                    "start_char": match.start(),
                    "end_char": match.end(),
                }
            )
        return lists
