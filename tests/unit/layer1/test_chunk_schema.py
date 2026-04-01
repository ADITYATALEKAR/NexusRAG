"""Tests for the chunk schema."""

import pytest
from pydantic import ValidationError

from src.layer1_contracts.schemas.chunk import Chunk, ChunkLocation


def test_chunk_schema_accepts_valid_payload() -> None:
    """A valid chunk payload should parse."""
    chunk = Chunk(
        id="chunk_123456",
        document_id="doc_123456",
        content="hello",
        location=ChunkLocation(start_char=0, end_char=5),
        sequence_number=0,
    )

    assert chunk.location.end_char == 5


def test_chunk_location_rejects_inverted_offsets() -> None:
    """Chunk locations must be forward-moving."""
    with pytest.raises(ValidationError):
        ChunkLocation(start_char=5, end_char=1)
