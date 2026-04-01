"""Contract serialization tests."""

from src.layer1_contracts.schemas.document import Document, DocumentType
from src.layer1_contracts.schemas.llm import LLMConfig, LLMRequest, Message, MessageRole
from src.layer1_contracts.schemas.security import SecurityDecision, SecurityDecisionType


def test_document_round_trip_serialization() -> None:
    """Documents should survive JSON round trips."""
    document = Document(id="doc_123456", content="hello", document_type=DocumentType.TXT)

    restored = Document.model_validate_json(document.model_dump_json())

    assert restored == document


def test_llm_request_round_trip_serialization() -> None:
    """LLM requests should survive JSON round trips."""
    request = LLMRequest(
        id="req-1",
        messages=[Message(role=MessageRole.USER, content="hello")],
        config=LLMConfig(model="mock-model"),
    )

    restored = LLMRequest.model_validate_json(request.model_dump_json())

    assert restored == request


def test_security_decision_round_trip_serialization() -> None:
    """Security decisions should survive JSON round trips."""
    decision = SecurityDecision(decision=SecurityDecisionType.ALLOW)

    restored = SecurityDecision.model_validate_json(decision.model_dump_json())

    assert restored == decision
