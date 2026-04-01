"""Dense retrieval over vector similarity."""

from __future__ import annotations

import math
import time
from typing import Protocol

import numpy as np

from src.layer1_contracts.interfaces.embedder import EmbedderInterface
from src.layer1_contracts.interfaces.vector_store import VectorStoreInterface
from src.layer1_contracts.schemas.retrieval import RetrievalCandidate, RetrievalScores, RetrievalSource
from src.layer1_contracts.schemas.retrieval_config import FilterConfig
from src.layer4_providers.stores.metadata.sqlite_adapter import SQLiteMetadataStore


class FeatureFlagReader(Protocol):
    """Minimal feature-flag protocol for lower-layer retrieval components."""

    def is_enabled(self, name: str) -> bool: ...


class DenseRetriever:
    """Retrieve candidates from the vector store."""

    def __init__(
        self,
        embedder: EmbedderInterface,
        vector_store: VectorStoreInterface,
        metadata_store: SQLiteMetadataStore,
        feature_flags: FeatureFlagReader | None = None,
        compression_quantizer: object | None = None,
    ) -> None:
        self.embedder = embedder
        self.vector_store = vector_store
        self.metadata_store = metadata_store
        self.feature_flags = feature_flags
        self.compression_quantizer = compression_quantizer
        self.last_query_embedding_time_ms = 0

    async def retrieve(
        self,
        query: str,
        top_k: int = 50,
        filter_config: FilterConfig | None = None,
    ) -> tuple[list[RetrievalCandidate], int]:
        """Retrieve candidates via dense vector search."""
        start = time.perf_counter()
        embedding_start = time.perf_counter()
        query_embedding = await self.embedder.embed_query(query)
        if self._compression_enabled():
            query_embedding = self._apply_compression([query_embedding])[0]
        self.last_query_embedding_time_ms = int((time.perf_counter() - embedding_start) * 1000)

        results = await self.vector_store.search(
            query_vector=query_embedding,
            top_k=self._overfetch_size(top_k, filter_config),
            filter=self._build_store_filter(filter_config),
        )

        candidates: list[RetrievalCandidate] = []
        for chunk_id, score, payload in results:
            chunk_meta = await self.metadata_store.get_chunk(chunk_id)
            if not self._matches_filter(chunk_id, chunk_meta, filter_config):
                continue

            meta = chunk_meta or {}
            payload = payload or {}
            raw_score = self._raw_score(score)
            candidates.append(
                RetrievalCandidate(
                    chunk_id=chunk_id,
                    document_id=meta.get("document_id", payload.get("document_id", "")),
                    content=meta.get("content", ""),
                    scores=RetrievalScores(dense_score=raw_score, final_score=raw_score),
                    source=RetrievalSource.DENSE,
                    rank=len(candidates),
                    document_title=meta.get("document_title"),
                    section_title=meta.get("section_title", payload.get("section_title")),
                    page_numbers=list(meta.get("page_numbers", payload.get("page_numbers", []))),
                )
            )
            if len(candidates) >= top_k:
                break

        latency_ms = int((time.perf_counter() - start) * 1000)
        return candidates, latency_ms

    def _build_store_filter(self, config: FilterConfig | None) -> dict | None:
        """Build a simple store-side pre-filter when possible."""
        if config and config.document_ids and len(config.document_ids) == 1:
            return {"document_id": config.document_ids[0]}
        return None

    def _overfetch_size(self, top_k: int, config: FilterConfig | None) -> int:
        """Overfetch when downstream filters may trim the result set."""
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
        """Apply dense-stage filters against stored metadata."""
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
        """Return the raw similarity score while handling NaN safely."""
        if math.isnan(score):
            return 0.0
        return float(score)

    def _compression_enabled(self) -> bool:
        """Return whether query embeddings should follow the compressed vector path."""
        if self.feature_flags is None or not self.feature_flags.is_enabled("vector_compression"):
            return False
        return self._codec_ready()

    def _codec_ready(self) -> bool:
        """Return whether the configured compression codec has fitted state."""
        if self.compression_quantizer is None:
            return False
        if hasattr(self.compression_quantizer, "is_fitted"):
            return bool(self.compression_quantizer.is_fitted)
        if hasattr(self.compression_quantizer, "min_vals"):
            return getattr(self.compression_quantizer, "min_vals") is not None
        if hasattr(self.compression_quantizer, "centroids"):
            return bool(getattr(self.compression_quantizer, "centroids"))
        return False

    def _apply_compression(self, vectors: list[list[float]]) -> list[list[float]]:
        """Quantize and restore vectors so retrieval follows the compressed path."""
        if self.compression_quantizer is None:
            return vectors
        array = np.asarray(vectors, dtype=np.float32)
        if hasattr(self.compression_quantizer, "quantize") and hasattr(self.compression_quantizer, "dequantize"):
            compressed = self.compression_quantizer.quantize(array)
            restored = self.compression_quantizer.dequantize(compressed)
        elif hasattr(self.compression_quantizer, "encode") and hasattr(self.compression_quantizer, "decode"):
            compressed = self.compression_quantizer.encode(array)
            restored = self.compression_quantizer.decode(compressed)
        else:
            return vectors
        return restored.astype(np.float32).tolist()
