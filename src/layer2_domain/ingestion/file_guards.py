"""File validation guards for ingestion."""

from __future__ import annotations

from pathlib import Path

from src.layer1_contracts.schemas.security import SecurityDecision, SecurityDecisionType, ThreatCategory

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md", ".html", ".csv", ".json"}
MAX_FILE_SIZE = 52_428_800
DANGEROUS_EXTENSIONS = {".exe", ".bat", ".sh", ".ps1", ".dll", ".so"}


class FileGuard:
    """Validate whether a file is safe and supported for ingestion."""

    def __init__(
        self,
        max_size: int = MAX_FILE_SIZE,
        allowed_extensions: set[str] | None = None,
    ) -> None:
        self.max_size = max_size
        self.allowed_extensions = allowed_extensions or ALLOWED_EXTENSIONS

    def validate(self, file_path: str, file_size: int) -> SecurityDecision:
        """Validate a file path and size."""
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext in DANGEROUS_EXTENSIONS:
            return SecurityDecision(
                decision=SecurityDecisionType.DENY,
                threat_category=ThreatCategory.MALFORMED,
                reason=f"Dangerous file extension: {ext}",
            )

        if ext not in self.allowed_extensions:
            return SecurityDecision(
                decision=SecurityDecisionType.DENY,
                threat_category=ThreatCategory.MALFORMED,
                reason=f"Unsupported file extension: {ext}",
            )

        if file_size > self.max_size:
            return SecurityDecision(
                decision=SecurityDecisionType.DENY,
                threat_category=ThreatCategory.OVERSIZED,
                reason=f"File exceeds {self.max_size} bytes",
            )

        return SecurityDecision(decision=SecurityDecisionType.ALLOW)
