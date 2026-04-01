"""Common regex patterns."""

IDENTIFIER_PATTERN = r"^[a-zA-Z0-9_-]+$"
SQL_INJECTION_PATTERN = r"(?i)\\b(union\\s+select|drop\\s+table|delete\\s+from|insert\\s+into)\\b"
PROMPT_INJECTION_PATTERN = (
    r"(?i)(ignore\\s+previous\\s+instructions|forget\\s+the\\s+rules|system\\s+prompt:)"
)
