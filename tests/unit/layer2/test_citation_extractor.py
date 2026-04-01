"""Unit tests for citation extraction and validation."""

from __future__ import annotations

from src.layer1_contracts.schemas.evidence import EvidenceBundle, EvidenceItem
from src.layer2_domain.citations.extractor import CitationExtractor
from src.layer2_domain.citations.validator import CitationValidator


def test_citation_extractor_maps_answer_references_to_evidence() -> None:
    """Citation extraction should map numeric references back to evidence items."""
    bundle = EvidenceBundle(
        query_id="query-1",
        items=[
            EvidenceItem(
                chunk_id="chunk-1",
                document_id="doc-1",
                content="Dense search uses embeddings.",
                citation_key="[1]",
                document_title="Dense",
                relevance_score=0.8,
            ),
            EvidenceItem(
                chunk_id="chunk-2",
                document_id="doc-2",
                content="Lexical search uses BM25.",
                citation_key="[2]",
                document_title="Lexical",
                relevance_score=0.8,
            ),
        ],
    )

    citations = CitationExtractor().extract(
        "Hybrid retrieval uses dense search [1] and lexical search [2].",
        bundle,
    )

    assert [citation.citation_key for citation in citations] == ["[1]", "[2]"]
    assert citations[0].chunk_id == "chunk-1"
    assert citations[1].chunk_id == "chunk-2"


def test_citation_validator_flags_uncited_claims() -> None:
    """Validation should catch long uncited claims in answers."""
    bundle = EvidenceBundle(
        query_id="query-1",
        items=[
            EvidenceItem(
                chunk_id="chunk-1",
                document_id="doc-1",
                content="Dense search uses embeddings.",
                citation_key="[1]",
                relevance_score=0.9,
            )
        ],
    )
    answer_text = (
        "Hybrid retrieval combines dense search and lexical search with fusion [1]. "
        "This sentence makes a much longer unsupported claim without any citation marker at all."
    )

    is_valid, issues = CitationValidator().validate(
        answer_text=answer_text,
        citations=CitationExtractor().extract(answer_text, bundle),
        evidence_bundle=bundle,
    )

    assert not is_valid
    assert any("Potentially uncited claim" in issue for issue in issues)
