"""LLM-assisted context generation for contextual indexing."""

from __future__ import annotations

import json
import re
from typing import Protocol

from src.layer1_contracts.schemas.contextual import DocumentContext
from src.layer1_contracts.schemas.document import Document
from src.layer1_contracts.schemas.chunk import Chunk
from src.layer1_contracts.schemas.llm import LLMConfig, LLMRequest, Message, MessageRole


class LLMCompletionService(Protocol):
    """Bounded protocol for LLM services that can complete requests."""

    async def complete(self, request: LLMRequest): ...


class ContextGenerator:
    """Generate compact document- and chunk-level context using an LLM."""

    def __init__(self, llm_service: LLMCompletionService) -> None:
        self.llm_service = llm_service

    async def generate_document_context(self, document: Document) -> DocumentContext:
        """Generate a short summary and topic list for a document."""
        prompt = (
            "Analyze document and return strict JSON with keys "
            '"summary" and "key_topics".\n\n'
            f"Document:\n{document.content[:2000]}"
        )
        response = await self.llm_service.complete(
            LLMRequest(
                id=f"ctx-{document.id}",
                messages=[Message(role=MessageRole.USER, content=prompt)],
                config=LLMConfig(model="gpt-4o-mini", temperature=0.0, max_tokens=300),
            )
        )

        try:
            payload = json.loads(response.content)
        except json.JSONDecodeError:
            payload = self._fallback_payload(document.content)

        summary = str(payload.get("summary") or self._fallback_payload(document.content)["summary"]).strip()
        key_topics = self._normalize_topics(payload.get("key_topics"), document.content)
        return DocumentContext(document_id=document.id, summary=summary, key_topics=key_topics)

    def generate_chunk_context(self, chunk: Chunk, doc_ctx: DocumentContext) -> str:
        """Generate a compact context header for one chunk."""
        parts = [f"Document: {doc_ctx.summary}"]
        if chunk.metadata.section_title:
            parts.append(f"Section: {chunk.metadata.section_title}")
        if chunk.metadata.section_hierarchy:
            parts.append(f"Hierarchy: {' > '.join(chunk.metadata.section_hierarchy)}")
        if doc_ctx.key_topics:
            parts.append(f"Topics: {', '.join(doc_ctx.key_topics[:3])}")
        return " | ".join(parts)

    def _normalize_topics(self, raw_topics: object, content: str) -> list[str]:
        """Normalize topic payloads from the LLM into a bounded list."""
        if isinstance(raw_topics, list):
            topics = [str(topic).strip() for topic in raw_topics if str(topic).strip()]
            if topics:
                return topics[:5]
        return self._fallback_payload(content)["key_topics"]

    def _fallback_payload(self, content: str) -> dict[str, object]:
        """Return a deterministic heuristic fallback when JSON parsing fails."""
        cleaned = " ".join(content.split())
        summary = cleaned[:200].strip() or "No summary available."
        topic_counts: dict[str, int] = {}
        for token in re.findall(r"[a-zA-Z]{4,}", content.lower()):
            topic_counts[token] = topic_counts.get(token, 0) + 1
        key_topics = [token for token, _ in sorted(topic_counts.items(), key=lambda item: (-item[1], item[0]))[:5]]
        return {"summary": summary, "key_topics": key_topics}
