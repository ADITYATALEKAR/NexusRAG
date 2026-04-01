"""Contract validation tests."""

import pytest
from pydantic import ValidationError

from src.layer1_contracts.schemas.document import Document
from src.layer1_contracts.schemas.llm import LLMUsage


def test_document_validation_rejects_bad_ids() -> None:
    """Document IDs should reject unsupported characters."""
    with pytest.raises(ValidationError):
        Document(id="bad id", content="hello", document_type="txt")


def test_llm_usage_validation_rejects_bad_totals() -> None:
    """LLM usage totals should be validated."""
    with pytest.raises(ValidationError):
        LLMUsage(prompt_tokens=2, completion_tokens=3, total_tokens=1)
