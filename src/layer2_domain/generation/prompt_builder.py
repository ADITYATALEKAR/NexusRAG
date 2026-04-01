"""Build prompts for answer generation."""

from __future__ import annotations

from src.layer1_contracts.schemas.evidence import EvidenceBundle, EvidenceItem
from src.layer1_contracts.schemas.generation import GenerationConfig
from src.layer1_contracts.schemas.llm import Message, MessageRole
from src.layer1_contracts.schemas.query import Query


class PromptBuilder:
    """Build prompts for grounded answer generation."""

    DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided evidence.

Rules:
1. Only use information from the provided evidence to answer
2. Cite your sources using the citation keys like [1], [2]
3. If the evidence doesn't contain enough information to answer, say so
4. Be concise and accurate
5. If evidence conflicts, acknowledge the discrepancy"""

    EVIDENCE_TEMPLATE = """
### Evidence {citation_key}
Source: {source_info}
Content: {content}
"""

    USER_TEMPLATE = """Based on the following evidence, answer this question: {query}

{evidence_block}

Provide a clear, well-cited answer:"""

    ABSTENTION_TEMPLATE = """Based on the following evidence, answer this question: {query}

{evidence_block}

If the evidence is insufficient to answer the question accurately, respond with:
"I cannot answer this question based on the available evidence because [reason]."

Otherwise, provide a clear, well-cited answer:"""

    def __init__(
        self,
        default_system_prompt: str | None = None,
        evidence_template: str | None = None,
        user_template: str | None = None,
        abstention_template: str | None = None,
    ) -> None:
        self.default_system_prompt = default_system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.evidence_template = evidence_template or self.EVIDENCE_TEMPLATE
        self.user_template = user_template or self.USER_TEMPLATE
        self.abstention_template = abstention_template or self.ABSTENTION_TEMPLATE

    def build(
        self,
        query: Query,
        evidence_bundle: EvidenceBundle,
        config: GenerationConfig,
        system_prompt_override: str | None = None,
    ) -> list[Message]:
        """Build the message sequence for answer generation."""
        evidence_block = self._format_evidence(evidence_bundle)
        if config.allow_abstention:
            user_content = self.abstention_template.format(query=query.text, evidence_block=evidence_block)
        else:
            user_content = self.user_template.format(query=query.text, evidence_block=evidence_block)

        return [
            Message(role=MessageRole.SYSTEM, content=system_prompt_override or self.default_system_prompt),
            Message(role=MessageRole.USER, content=user_content),
        ]

    def _format_evidence(self, bundle: EvidenceBundle) -> str:
        return "\n".join(
            self.evidence_template.format(
                citation_key=item.citation_key,
                source_info=self._format_source(item),
                content=item.content,
            )
            for item in bundle.items
        )

    def _format_source(self, item: EvidenceItem) -> str:
        parts: list[str] = []
        if item.document_title:
            parts.append(item.document_title)
        if item.section_title:
            parts.append(f"Section: {item.section_title}")
        if item.page_numbers:
            parts.append(f"Page(s): {', '.join(map(str, item.page_numbers))}")
        return " | ".join(parts) if parts else "Unknown source"
