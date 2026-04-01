"""Tests for the document schema."""

import pytest
from pydantic import ValidationError

from src.layer1_contracts.schemas.document import Document, DocumentType


def test_document_schema_accepts_valid_payload() -> None:
    """A valid document payload should parse."""
    document = Document(id="doc_123456", content="hello", document_type=DocumentType.TXT)

    assert document.id == "doc_123456"


def test_document_schema_forbids_extra_fields() -> None:
    """Unexpected fields should be rejected."""
    with pytest.raises(ValidationError):
        Document(id="doc_123456", content="hello", document_type="txt", unknown=True)
