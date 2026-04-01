"""Generation evaluation metrics."""

from __future__ import annotations

from src.layer1_contracts.interfaces.embedder import EmbedderInterface
from src.layer1_contracts.schemas.answer import Answer, AnswerStatus, Citation
from src.layer1_contracts.schemas.evaluation import EvalDatasetItem, GenerationMetricsResult


class GenerationMetrics:
    """Calculate generation quality metrics."""

    def __init__(self, embedder: EmbedderInterface | None = None) -> None:
        self.embedder = embedder

    async def faithfulness(self, answer: str, evidence: list[str]) -> float:
        """Measure whether answer claims are grounded in evidence."""
        if not evidence:
            return 0.0
        sentences = [sentence.strip() for sentence in answer.split(".") if sentence.strip()]
        if not sentences:
            return 0.0
        evidence_words = set(" ".join(evidence).lower().split())
        supported = 0
        for sentence in sentences:
            words = set(sentence.lower().split())
            overlap = len(words & evidence_words) / float(len(words)) if words else 0.0
            if overlap > 0.3:
                supported += 1
        return supported / float(len(sentences))

    async def relevance(self, answer: str, query: str) -> float:
        """Measure whether the answer addresses the query."""
        if self.embedder is None:
            query_words = set(query.lower().split())
            answer_words = set(answer.lower().split())
            return len(query_words & answer_words) / float(len(query_words)) if query_words else 0.0
        return self._cosine_similarity(
            await self.embedder.embed_query(query),
            await self.embedder.embed_query(answer),
        )

    def citation_precision(self, citations: list[Citation], expected: list[str]) -> float:
        """Correct citations divided by total citations."""
        if not citations:
            return 1.0 if not expected else 0.0
        cited_chunks = {citation.chunk_id for citation in citations}
        expected_set = set(expected)
        return len(cited_chunks & expected_set) / float(len(citations))

    def citation_recall(self, citations: list[Citation], expected: list[str]) -> float:
        """Correct citations divided by expected citations."""
        if not expected:
            return 1.0
        cited_chunks = {citation.chunk_id for citation in citations}
        expected_set = set(expected)
        return len(cited_chunks & expected_set) / float(len(expected_set))

    async def answer_similarity(self, answer: str, expected: str) -> float:
        """Semantic similarity to the expected answer."""
        if not expected:
            return 1.0
        if self.embedder is None:
            answer_words = set(answer.lower().split())
            expected_words = set(expected.lower().split())
            union = answer_words | expected_words
            return len(answer_words & expected_words) / float(len(union)) if union else 0.0
        return self._cosine_similarity(
            await self.embedder.embed_query(answer),
            await self.embedder.embed_query(expected),
        )

    async def evaluate(
        self,
        answer: Answer,
        item: EvalDatasetItem,
        evidence: list[str],
    ) -> GenerationMetricsResult:
        """Evaluate one answer against a golden dataset item."""
        return GenerationMetricsResult(
            faithfulness=await self.faithfulness(answer.text, evidence),
            relevance=await self.relevance(answer.text, item.query),
            citation_precision=self.citation_precision(answer.citations, item.expected_citations),
            citation_recall=self.citation_recall(answer.citations, item.expected_citations),
            answer_similarity=await self.answer_similarity(answer.text, item.expected_answer or ""),
            abstention_accuracy=(
                1.0
                if (answer.status == AnswerStatus.ABSTAINED) == (not item.expected_answer)
                else 0.0
            ),
        )

    @staticmethod
    def _cosine_similarity(left: list[float], right: list[float]) -> float:
        """Return cosine similarity between two vectors."""
        dot = sum(a * b for a, b in zip(left, right))
        left_norm = sum(value * value for value in left) ** 0.5
        right_norm = sum(value * value for value in right) ** 0.5
        return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0
