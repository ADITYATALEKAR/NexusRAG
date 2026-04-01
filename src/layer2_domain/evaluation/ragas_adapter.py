"""RAGAS-style adapter over the shared LLM runtime."""

from __future__ import annotations

from datetime import datetime, timezone

from src.layer1_contracts.schemas.llm import LLMConfig, LLMRequest, Message, MessageRole
from src.layer2_domain.failover.service import FailoverService


class RAGASAdapter:
    """Adapter for RAGAS-like evaluation prompts."""

    def __init__(self, llm_service: FailoverService) -> None:
        self.llm_service = llm_service

    async def context_precision(self, query: str, contexts: list[str], ground_truth: str) -> float:
        """Estimate how much retrieved context is relevant."""
        prompt = (
            "Rate each context's relevance to answering the query (1=relevant, 0=not).\n\n"
            f"Query: {query}\n"
            f"Ground Truth Answer: {ground_truth}\n\n"
            "Contexts:\n"
            f"{chr(10).join(f'{index + 1}. {context[:200]}...' for index, context in enumerate(contexts))}\n\n"
            "Respond with comma-separated 0s and 1s for each context:"
        )
        response = await self._call_llm(prompt)
        try:
            ratings = [int(value.strip()) for value in response.split(",") if value.strip()]
            return sum(ratings) / float(len(ratings)) if ratings else 0.0
        except ValueError:
            return 0.5

    async def context_recall(self, contexts: list[str], ground_truth: str) -> float:
        """Estimate how much of the ground truth is recoverable from contexts."""
        prompt = (
            "What fraction of the ground truth answer can be derived from these contexts?\n\n"
            f"Ground Truth: {ground_truth}\n\n"
            "Contexts:\n"
            f"{chr(10).join(f'{index + 1}. {context[:200]}...' for index, context in enumerate(contexts))}\n\n"
            "Respond with a single number between 0.0 and 1.0:"
        )
        response = await self._call_llm(prompt)
        try:
            return float(response.strip())
        except ValueError:
            return 0.5

    async def faithfulness(self, answer: str, contexts: list[str]) -> float:
        """Estimate whether claims in the answer are supported by contexts."""
        prompt = (
            "Extract claims from the answer, then check if each is supported by the contexts.\n\n"
            f"Answer: {answer}\n\n"
            "Contexts:\n"
            f"{chr(10).join(f'{index + 1}. {context[:200]}...' for index, context in enumerate(contexts))}\n\n"
            "What fraction of claims are supported? Respond with a single number 0.0-1.0:"
        )
        response = await self._call_llm(prompt)
        try:
            return float(response.strip())
        except ValueError:
            return 0.5

    async def answer_relevancy(self, query: str, answer: str) -> float:
        """Estimate whether the answer addresses the query."""
        prompt = (
            "Rate how well this answer addresses the query (0.0-1.0):\n\n"
            f"Query: {query}\n"
            f"Answer: {answer}\n\n"
            "Single number 0.0-1.0:"
        )
        response = await self._call_llm(prompt)
        try:
            return float(response.strip())
        except ValueError:
            return 0.5

    async def _call_llm(self, prompt: str) -> str:
        """Call the shared LLM runtime for evaluation prompts."""
        response = await self.llm_service.execute(
            LLMRequest(
                id=f"ragas-{int(datetime.now(timezone.utc).timestamp() * 1000)}",
                messages=[Message(role=MessageRole.USER, content=prompt)],
                config=LLMConfig(model="gpt-4o-mini", temperature=0.0, max_tokens=100),
            )
        )
        return response.content
