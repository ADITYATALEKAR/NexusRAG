"""Mock reranker adapter."""

from __future__ import annotations

from typing import Optional

from src.layer1_contracts.interfaces.reranker import RerankerInterface


class MockReranker(RerankerInterface):
    """Deterministic mock reranker that rewards overlap and concise relevance."""

    def __init__(self, model: str = "mock-reranker") -> None:
        self._model = model

    @property
    def model(self) -> str:
        """Return the configured model name."""
        return self._model

    async def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: Optional[int] = None,
    ) -> list[tuple[int, float]]:
        """Rank documents with a deterministic overlap-based heuristic."""
        query_words = set(query.lower().split())
        ranked: list[tuple[int, float]] = []
        for index, document in enumerate(documents):
            document_words = set(document.lower().split())
            overlap = len(query_words & document_words) / len(query_words) if query_words else 0.0
            exact_phrase_bonus = 0.15 if query.lower() in document.lower() else 0.0
            ideal_length = 200
            length_penalty = 1.0 - abs(len(document) - ideal_length) / 1000
            length_penalty = max(0.5, min(1.0, length_penalty))
            score = overlap * 0.7 + length_penalty * 0.15 + exact_phrase_bonus
            ranked.append((index, min(score, 1.0)))

        ranked.sort(key=lambda item: item[1], reverse=True)
        if top_k is not None:
            ranked = ranked[:top_k]
        return ranked

    async def health_check(self) -> bool:
        """Return whether the mock reranker is healthy."""
        return True
