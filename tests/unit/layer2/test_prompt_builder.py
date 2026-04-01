"""Unit tests for prompt construction."""

from __future__ import annotations

from src.layer1_contracts.schemas.evidence import EvidenceBundle, EvidenceItem
from src.layer1_contracts.schemas.generation import GenerationConfig
from src.layer1_contracts.schemas.query import Query
from src.layer1_contracts.schemas.llm import MessageRole
from src.layer2_domain.generation.prompt_builder import PromptBuilder


def test_prompt_builder_formats_evidence_with_citations() -> None:
    """Prompt builder should render evidence blocks and source metadata."""
    builder = PromptBuilder()
    bundle = EvidenceBundle(
        query_id="query-1",
        items=[
            EvidenceItem(
                chunk_id="chunk-1",
                document_id="doc-1",
                content="Hybrid retrieval combines dense and lexical search.",
                citation_key="[1]",
                document_title="Architecture",
                section_title="Retrieval",
                page_numbers=[3],
                relevance_score=0.9,
            )
        ],
    )

    messages = builder.build(
        query=Query(id="query-1", text="What is hybrid retrieval?"),
        evidence_bundle=bundle,
        config=GenerationConfig(allow_abstention=True),
    )

    assert len(messages) == 2
    assert messages[0].role == MessageRole.SYSTEM
    assert "Only use information from the provided evidence" in messages[0].content
    assert "### Evidence [1]" in messages[1].content
    assert "Source: Architecture | Section: Retrieval | Page(s): 3" in messages[1].content
    assert "What is hybrid retrieval?" in messages[1].content
    assert "I cannot answer this question based on the available evidence because [reason]." in messages[1].content
