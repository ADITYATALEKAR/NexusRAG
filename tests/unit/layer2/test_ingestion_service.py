"""Tests for ingestion services."""

from pathlib import Path

from src.layer1_contracts.schemas.security import SecurityDecisionType, ThreatCategory
from src.layer2_domain.ingestion.checksum import compute_checksum, compute_content_hash
from src.layer2_domain.ingestion.file_guards import FileGuard, MAX_FILE_SIZE
from src.layer2_domain.ingestion.service import IngestionService


def test_file_guard_rejects_exe() -> None:
    """Dangerous executable extensions should be denied."""
    decision = FileGuard().validate("malware.exe", 100)

    assert decision.decision == SecurityDecisionType.DENY
    assert decision.threat_category == ThreatCategory.MALFORMED


def test_file_guard_rejects_oversized() -> None:
    """Oversized files should be denied before parsing."""
    decision = FileGuard(max_size=10).validate("document.pdf", 11)

    assert decision.decision == SecurityDecisionType.DENY
    assert decision.threat_category == ThreatCategory.OVERSIZED


def test_checksum_deterministic(tmp_path: Path) -> None:
    """Checksums should be deterministic for the same content."""
    file_path = tmp_path / "sample.txt"
    file_path.write_text("vectorcore", encoding="utf-8")

    first = compute_checksum(str(file_path))
    second = compute_checksum(str(file_path))

    assert first == second
    assert first == compute_content_hash(b"vectorcore")


def test_ingestion_service_creates_request_from_existing_file(tmp_path: Path) -> None:
    """Ingestion service should extract metadata and create a request."""
    file_path = tmp_path / "note.txt"
    file_path.write_text("hello", encoding="utf-8")

    request = IngestionService().create_request(str(file_path))

    assert request.file_metadata.filename == "note.txt"
    assert request.file_metadata.file_size_bytes <= MAX_FILE_SIZE
