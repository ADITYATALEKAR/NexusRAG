"""Formatting for structured retrieval results."""

from __future__ import annotations


class StructuredResultFormatter:
    """Format tabular results into a compact natural-language answer."""

    def format(self, query: str, rows: list[dict[str, object]], columns: list[str]) -> str:
        """Return a compact answer string for structured results."""
        if not rows:
            return "No results found for the query."

        if len(rows) == 1 and len(columns) == 1:
            value = list(rows[0].values())[0]
            return f"The result is: {value}"

        if len(rows) == 1:
            parts = [f"{column}: {rows[0][column]}" for column in columns]
            return "Result: " + ", ".join(parts)

        summary = f"Found {len(rows)} results.\n\n"
        for index, row in enumerate(rows[:5]):
            parts = [f"{column}: {row[column]}" for column in columns[:3]]
            summary += f"{index + 1}. " + ", ".join(parts) + "\n"
        if len(rows) > 5:
            summary += f"\n... and {len(rows) - 5} more results."
        return summary
