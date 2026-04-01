"""Unit tests for abstention checks."""

from __future__ import annotations

from src.layer1_contracts.schemas.evidence import EvidenceBundle, EvidenceItem
from src.layer2_domain.generation.abstention import AbstentionChecker


def test_abstention_triggers_on_insufficient_evidence() -> None:
    """Abstention should trigger when too little evidence is available."""
    checker = AbstentionChecker(min_evidence_items=1)
    should_abstain, reason = checker.should_abstain_before_generation(
        EvidenceBundle(query_id="query-1", items=[])
    )

    assert should_abstain is True
    assert reason is not None
    assert reason.value == "insufficient_evidence"


def test_abstention_detects_model_abstention_language() -> None:
    """Post-generation abstention phrases should be detected."""
    checker = AbstentionChecker()

    abstained, reason = checker.detect_abstention_in_response(
        "I cannot answer this question because there is not enough information in the evidence."
    )

    assert abstained is True
    assert reason is not None
    assert reason.value == "insufficient_evidence"
