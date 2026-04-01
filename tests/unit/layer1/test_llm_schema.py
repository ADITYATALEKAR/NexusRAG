"""Tests for the LLM schemas."""

import pytest
from pydantic import ValidationError

from src.layer1_contracts.schemas.llm import LLMConfig, LLMRequest, LLMUsage, Message, MessageRole


def test_llm_request_accepts_valid_payload() -> None:
    """A valid LLM request should parse."""
    request = LLMRequest(
        id="req-1",
        messages=[Message(role=MessageRole.USER, content="hello")],
        config=LLMConfig(model="mock-model"),
    )

    assert request.config.model == "mock-model"


def test_llm_usage_validates_total_tokens() -> None:
    """Token totals must add up."""
    with pytest.raises(ValidationError):
        LLMUsage(prompt_tokens=1, completion_tokens=2, total_tokens=10)
