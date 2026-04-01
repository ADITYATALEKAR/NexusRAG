"""File metadata extraction."""

from __future__ import annotations

from datetime import datetime, timezone
import mimetypes
from pathlib import Path

from src.layer1_contracts.schemas.ingestion import FileMetadata

try:
    import magic  # type: ignore
except ImportError:  # pragma: no cover - optional dependency fallback
    magic = None


class MetadataExtractor:
    """Extract filesystem and MIME metadata for ingestion."""

    def extract(self, file_path: str) -> FileMetadata:
        """Extract file metadata from a path."""
        path = Path(file_path)
        stat = path.stat()
        mime_type = self._detect_mime_type(path)
        return FileMetadata(
            filename=path.name,
            file_size_bytes=stat.st_size,
            mime_type=mime_type,
            extension=path.suffix.lower(),
            created_at=datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc),
            modified_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
        )

    def _detect_mime_type(self, path: Path) -> str | None:
        """Detect MIME type using libmagic when available, otherwise mimetypes."""
        if magic is not None:
            try:
                return magic.from_file(str(path), mime=True)
            except Exception:  # noqa: BLE001
                pass
        guessed, _ = mimetypes.guess_type(path.name)
        return guessed
