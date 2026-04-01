"""Unit tests for the Phase 5 query classifier."""

from __future__ import annotations

from src.layer1_contracts.schemas.query import QueryType
from src.layer1_contracts.schemas.query_understanding import QueryIntent
from src.layer2_domain.query_understanding.classifier import QueryClassifier


def test_query_classifier_accuracy_on_phase5_examples() -> None:
    """The classifier should meet the Phase 5 >80% accuracy bar on a smoke set."""
    classifier = QueryClassifier()
    cases = [
        ('"RFC 9110"', QueryType.KEYWORD),
        ("Explain hybrid retrieval for enterprise search", QueryType.SEMANTIC),
        ("How many documents are indexed?", QueryType.STRUCTURED),
        ("Compare Python vs Go for backend services", QueryType.COMPARATIVE),
        ("Who is the CEO of the company that made Pixel?", QueryType.MULTI_HOP),
    ]

    correct = sum(1 for query_text, expected in cases if classifier.classify(query_text).query_type == expected)
    assert correct / len(cases) >= 0.8


def test_query_classifier_generates_comparative_sub_queries() -> None:
    """Comparative queries should request bounded decomposition."""
    classifier = QueryClassifier()

    analysis = classifier.classify("Compare Python vs Go for backend APIs")

    assert analysis.query_type == QueryType.COMPARATIVE
    assert analysis.intent == QueryIntent.COMPARATIVE
    assert analysis.requires_decomposition is True
    assert len(analysis.sub_queries) == 3
    assert any(entity.text == "Python" for entity in analysis.entities)
