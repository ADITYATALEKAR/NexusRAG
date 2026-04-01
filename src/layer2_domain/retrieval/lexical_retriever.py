"""Lexical retrieval over BM25 search."""

from __future__ import annotations

import math
import time

from src.layer1_contracts.interfaces.lexical_store import LexicalStoreInterface
from src.layer1_contracts.schemas.retrieval import RetrievalCandidate, RetrievalScores, RetrievalSource
from src.layer1_contracts.schemas.retrieval_config import FilterConfig
from src.layer4_providers.stores.metadata.sqlite_adapter import SQLiteMetadataStore


class LexicalRetriever:
    """Retrieve candidates from the lexical index."""

    def __init__(
        self,
        lexical_store: LexicalStoreInterface,
        metadata_store: SQLiteMetadataStore,
    ) -> None:
        self.lexical_store = lexical_store
        self.metadata_store = metadata_store

    async def retrieve(
        self,
        query: str,
        top_k: int = 50,
        filter_config: FilterConfig | None = None,
    ) -> tuple[list[RetrievalCandidate], int]:
        """Retrieve candidates via BM25-style lexical search."""
        start = time.perf_counter()
        results = await self.lexical_store.search(
            query,
            top_k=self._overfetch_size(top_k, filter_config),
            filter=self._build_store_filter(filter_config),
        )

        candidates: list[RetrievalCandidate] = []
        for chunk_id, score in results:
            chunk_meta = await self.metadata_store.get_chunk(chunk_id)
            if not self._matches_filter(chunk_id, chunk_meta, filter_config):
                continue

            meta = chunk_meta or {}
            raw_score = self._raw_score(score)
            candidates.append(
                RetrievalCandidate(
                    chunk_id=chunk_id,
                    document_id=meta.get("document_id", ""),
                    content=meta.get("content", ""),
                    scores=RetrievalScores(lexical_score=raw_score, final_score=raw_score),
                    source=RetrievalSource.LEXICAL,
                    rank=len(candidates),
                    document_title=meta.get("document_title"),
                    section_title=meta.get("section_title"),
                    page_numbers=list(meta.get("page_numbers", [])),
                )
            )
            if len(candidates) >= top_k:
                break

        latency_ms = int((time.perf_counter() - start) * 1000)
        return candidates, latency_ms

    def _build_store_filter(self, config: FilterConfig | None) -> dict | None:
        """Build a simple lexical-store filter when possible."""
        if config and config.document_ids and len(config.document_ids) == 1:
            return {"document_id": config.document_ids[0]}
        return None

    def _overfetch_size(self, top_k: int, config: FilterConfig | None) -> int:
        """Overfetch when filters are likely to prune results."""
        if config is None:
            return top_k
        if any(
            [
                config.document_ids,
                config.document_types,
                config.tags,
                config.date_from,
                config.date_to,
                config.min_trust_score is not None,
                config.exclude_chunk_ids,
            ]
        ):
            return min(max(top_k * 4, top_k), 500)
        return top_k

    def _matches_filter(
        self,
        chunk_id: str,
        chunk_meta: dict | None,
        config: FilterConfig | None,
    ) -> bool:
        """Apply lexical-stage filters against metadata."""
        if config is None:
            return True
        meta = chunk_meta or {}
        if config.exclude_chunk_ids and chunk_id in config.exclude_chunk_ids:
            return False
        if config.document_ids and meta.get("document_id") not in config.document_ids:
            return False
        return True

    @staticmethod
    def _raw_score(score: float) -> float:
        """Return the raw BM25 score while handling NaN safely."""
        if math.isnan(score):
            return 0.0
        return float(score)
