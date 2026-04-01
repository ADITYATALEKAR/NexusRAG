"""Tests for Phase 2 chunking strategies."""

from __future__ import annotations

from src.layer1_contracts.schemas.chunking import ChunkingConfig, ChunkingRequest, ChunkingStrategy
from src.layer1_contracts.schemas.document import DocumentMetadata
from src.layer1_contracts.schemas.normalization import ChunkPrecursor, NormalizedDocument, NormalizedSection
from src.layer2_domain.chunking.service import ChunkingService


def build_normalized_inputs() -> tuple[NormalizedDocument, list[ChunkPrecursor]]:
    """Build a repeatable normalized document and precursor set for chunking tests."""
    section_a = "VectorCore keeps traceability intact. " * 6
    section_b = "Chunking should preserve page numbers and section hierarchy. " * 5
    content = f"{section_a}\n\n{section_b}"
    split_point = len(section_a)
    precursors = [
        ChunkPrecursor(
            id="pre-section-0",
            document_id="norm-doc-1",
            content=section_a,
            section_id="section-0",
            section_title="Overview",
            section_hierarchy=["Overview"],
            start_char=0,
            end_char=len(section_a),
            page_numbers=[1],
            suggested_split_points=[90],
            is_complete_section=False,
        ),
        ChunkPrecursor(
            id="pre-section-1",
            document_id="norm-doc-1",
            content=section_b,
            section_id="section-1",
            section_title="Traceability",
            section_hierarchy=["Overview", "Traceability"],
            start_char=split_point + 2,
            end_char=split_point + 2 + len(section_b),
            page_numbers=[2],
            suggested_split_points=[80],
            is_complete_section=False,
        ),
    ]
    normalized_doc = NormalizedDocument(
        id="norm-doc-1",
        original_document_id="doc-1",
        content=content,
        sections=[
            NormalizedSection(
                id="section-0",
                title="Overview",
                level=1,
                content=section_a,
                start_char=0,
                end_char=len(section_a),
                page_numbers=[1],
            ),
            NormalizedSection(
                id="section-1",
                title="Traceability",
                level=2,
                content=section_b,
                start_char=split_point + 2,
                end_char=split_point + 2 + len(section_b),
                page_numbers=[2],
                parent_id="section-0",
            ),
        ],
        metadata=DocumentMetadata(page_count=2, word_count=len(content.split()), char_count=len(content)),
        page_count=2,
        word_count=len(content.split()),
        char_count=len(content),
    )
    return normalized_doc, precursors


async def chunk_with_strategy(strategy: ChunkingStrategy):
    """Run the chunking service with one configured strategy."""
    normalized_doc, precursors = build_normalized_inputs()
    service = ChunkingService(
        default_config=ChunkingConfig(
            strategy=strategy,
            target_size=120,
            min_size=40,
            max_size=180,
            overlap=24,
        )
    )
    request = ChunkingRequest(
        id=f"chunk-{strategy.value}",
        document_id=normalized_doc.original_document_id,
        normalized_content=normalized_doc.content,
        chunk_precursors=precursors,
        config=service.default_config,
    )
    return await service.chunk(request)


def test_fixed_size_strategy_preserves_traceability() -> None:
    """Fixed-size chunking should retain source offsets and page numbers."""
    normalized_doc, precursors = build_normalized_inputs()
    service = ChunkingService(
        default_config=ChunkingConfig(
            strategy=ChunkingStrategy.FIXED_SIZE,
            target_size=100,
            min_size=40,
            max_size=140,
            overlap=16,
        )
    )
    result = __import__("asyncio").run(
        service.chunk(
            ChunkingRequest(
                id="chunk-fixed",
                document_id=normalized_doc.original_document_id,
                normalized_content=normalized_doc.content,
                chunk_precursors=precursors,
                config=service.default_config,
            )
        )
    )

    assert result.total_chunks >= 2
    assert all(chunk.document_id == "doc-1" for chunk in result.chunks)
    assert all(chunk.location.end_char >= chunk.location.start_char for chunk in result.chunks)
    assert any(chunk.metadata.page_numbers == [1] for chunk in result.chunks)


def test_semantic_strategy_uses_precursor_metadata() -> None:
    """Semantic chunking should keep section titles and hierarchy metadata."""
    result = __import__("asyncio").run(chunk_with_strategy(ChunkingStrategy.SEMANTIC))

    assert result.total_chunks >= 2
    assert any(chunk.metadata.section_title == "Overview" for chunk in result.chunks)
    assert any(chunk.metadata.section_hierarchy == ["Overview", "Traceability"] for chunk in result.chunks)


def test_hierarchical_strategy_creates_parent_child_relationships() -> None:
    """Hierarchical chunking should add parent chunks with linked children."""
    result = __import__("asyncio").run(chunk_with_strategy(ChunkingStrategy.HIERARCHICAL))

    parent_chunks = [chunk for chunk in result.chunks if chunk.child_chunk_ids]
    child_chunks = [chunk for chunk in result.chunks if chunk.parent_chunk_id]

    assert parent_chunks
    assert child_chunks
    assert any(parent.id == child.parent_chunk_id for parent in parent_chunks for child in child_chunks)


def test_chunk_sizing_is_stable_across_runs() -> None:
    """Repeated chunking runs should yield the same chunk boundaries and content."""
    first = __import__("asyncio").run(chunk_with_strategy(ChunkingStrategy.SEMANTIC))
    second = __import__("asyncio").run(chunk_with_strategy(ChunkingStrategy.SEMANTIC))

    first_signature = [
        (chunk.content, chunk.location.start_char, chunk.location.end_char, chunk.metadata.section_title)
        for chunk in first.chunks
    ]
    second_signature = [
        (chunk.content, chunk.location.start_char, chunk.location.end_char, chunk.metadata.section_title)
        for chunk in second.chunks
    ]

    assert first_signature == second_signature
