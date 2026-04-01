"""Tests for typed identifiers."""

from src.layer0_core.ids.base import ChunkId, DocumentId


def test_id_generation_is_sortable_and_typed() -> None:
    """Generated IDs should be usable and type-sensitive."""
    document_id = DocumentId.generate()
    chunk_id = ChunkId.generate()

    assert "-" in document_id.value
    assert str(document_id) == document_id.value
    assert document_id != chunk_id
    assert hash(document_id) != hash(chunk_id)


def test_id_validation_rejects_empty_strings() -> None:
    """IDs must be non-empty strings."""
    try:
        DocumentId("")
    except ValueError as error:
        assert "non-empty string" in str(error)
    else:
        raise AssertionError("Expected ValueError")
