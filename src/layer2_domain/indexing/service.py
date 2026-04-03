"""Indexing service."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

import numpy as np

from src.layer1_contracts.interfaces.embedder import EmbedderInterface
from src.layer1_contracts.interfaces.lexical_store import LexicalStoreInterface
from src.layer1_contracts.interfaces.metadata_store import MetadataStoreInterface
from src.layer1_contracts.interfaces.vector_store import VectorStoreInterface
from src.layer1_contracts.schemas.chunk import Chunk
from src.layer1_contracts.schemas.document import Document
from src.layer1_contracts.schemas.feature_flags import BenchmarkResult
from src.layer1_contracts.schemas.indexing import IndexState, IndexStatus, IndexingResult
from src.layer2_domain.compression.benchmark import CompressionBenchmark
from src.layer2_domain.contextual_indexing.enricher import ChunkContextEnricher
from src.layer2_domain.indexing.job_manager import IndexJobManager


class FeatureFlagRuntime(Protocol):
    """Lower-layer feature flag protocol used by indexing."""

    def is_enabled(self, name: str) -> bool: ...
    def update_benchmark(self, name: str, result: BenchmarkResult) -> None: ...


class IndexingService:
    """Generate embeddings and persist chunks into vector, lexical, and metadata stores."""

    def __init__(
        self,
        embedder: EmbedderInterface,
        vector_store: VectorStoreInterface,
        lexical_store: LexicalStoreInterface,
        metadata_store: MetadataStoreInterface,
        batch_size: int = 32,
        job_manager: IndexJobManager | None = None,
        feature_flags: FeatureFlagRuntime | None = None,
        contextual_enricher: ChunkContextEnricher | None = None,
        compression_quantizer: object | None = None,
        compression_state_path: str | None = None,
        compression_min_recall: float = 0.98,
        compression_method: str = "scalar",
    ) -> None:
        self.embedder = embedder
        self.vector_store = vector_store
        self.lexical_store = lexical_store
        self.metadata_store = metadata_store
        self.batch_size = batch_size
        self.job_manager = job_manager or IndexJobManager()
        self.feature_flags = feature_flags
        self.contextual_enricher = contextual_enricher
        self.compression_quantizer = compression_quantizer
        self.compression_state_path = Path(compression_state_path) if compression_state_path else None
        self.compression_min_recall = compression_min_recall
        self.compression_method = compression_method

    async def index_chunks(
        self,
        chunks: list[Chunk],
        document_checksum: str,
        document: Document | None = None,
    ) -> IndexingResult:
        """Index chunks into the configured storage backends."""
        start = datetime.now(timezone.utc)
        if not chunks:
            return IndexingResult(
                job_id="idx-empty",
                document_id="",
                status=IndexStatus.COMPLETED,
                chunks_indexed=0,
                vector_index_time_ms=0,
                lexical_index_time_ms=0,
                total_time_ms=0,
            )

        job = self.job_manager.create_job(
            document_id=chunks[0].document_id,
            chunk_ids=[chunk.id for chunk in chunks],
            vector_store_id=getattr(self.vector_store, "collection", self.vector_store.__class__.__name__),
            lexical_store_id=getattr(self.lexical_store, "db_path", self.lexical_store.__class__.__name__),
        )
        errors: list[str] = []
        vector_time_ms = 0
        lexical_time_ms = 0
        all_embeddings: list[list[float]] = []
        contextual_lookup: dict[str, object] = {}

        try:
            self.job_manager.transition(job.id, IndexStatus.EMBEDDING)
            embedding_texts = await self._prepare_embedding_texts(chunks, document)
            contextual_lookup = embedding_texts[1]
            for index in range(0, len(chunks), self.batch_size):
                batch = chunks[index : index + self.batch_size]
                texts = embedding_texts[0][index : index + self.batch_size]
                embeddings = await self.embedder.embed(texts)
                all_embeddings.extend(embeddings)

                for chunk, embedding in zip(batch, embeddings):
                    chunk.embedding = embedding
                    chunk.embedding_model = self.embedder.model

            all_embeddings = self._maybe_apply_vector_compression(all_embeddings)
            for chunk, embedding in zip(chunks, all_embeddings):
                chunk.embedding = embedding
        except Exception as error:  # noqa: BLE001
            errors.append(f"Embedding failed: {error}")
            if job.status != IndexStatus.FAILED:
                self.job_manager.fail_job(job.id, str(error))

        try:
            for chunk in chunks:
                await self.metadata_store.save_chunk(chunk)

            await self.metadata_store.save_index_state(
                IndexState(
                    document_id=chunks[0].document_id,
                    document_checksum=document_checksum,
                    indexed_at=datetime.now(timezone.utc),
                    chunk_count=len(chunks),
                    embedding_model=self.embedder.model,
                )
            )
        except Exception as error:  # noqa: BLE001
            errors.append(f"Metadata persistence failed: {error}")
            if job.status != IndexStatus.FAILED:
                self.job_manager.fail_job(job.id, str(error))

        if job.status != IndexStatus.FAILED:
            try:
                self.job_manager.transition(job.id, IndexStatus.VECTOR_INDEXING)
                vector_start = datetime.now(timezone.utc)
                ids = [chunk.id for chunk in chunks]
                metadata = [
                    {
                        "document_id": chunk.document_id,
                        "document_title": chunk.metadata.document_title or "",
                        "document_type": chunk.metadata.document_type or "",
                        "tags": list(chunk.metadata.tags),
                        "trust_score": chunk.metadata.trust_score,
                        "section_title": chunk.metadata.section_title or "",
                        "page_numbers": list(chunk.metadata.page_numbers),
                        "contextual": chunk.id in contextual_lookup,
                        "context_source": getattr(contextual_lookup.get(chunk.id), "context_source", None),
                        "context_tokens": getattr(contextual_lookup.get(chunk.id), "context_tokens", 0),
                        "vector_compressed": self._compression_enabled(),
                        "compression_method": self.compression_method if self._compression_enabled() else None,
                    }
                    for chunk in chunks
                ]
                await self.vector_store.insert(ids, all_embeddings, metadata)
                vector_time_ms = int((datetime.now(timezone.utc) - vector_start).total_seconds() * 1000)
            except Exception as error:  # noqa: BLE001
                errors.append(f"Vector indexing failed: {error}")

        if job.status != IndexStatus.FAILED:
            try:
                self.job_manager.transition(job.id, IndexStatus.LEXICAL_INDEXING)
                lexical_start = datetime.now(timezone.utc)
                for chunk in chunks:
                    await self.lexical_store.index(
                        chunk.id,
                        chunk.content,
                        {
                            "document_id": chunk.document_id,
                            "section_title": chunk.metadata.section_title or "",
                        },
                    )
                lexical_time_ms = int((datetime.now(timezone.utc) - lexical_start).total_seconds() * 1000)
            except Exception as error:  # noqa: BLE001
                errors.append(f"Lexical indexing failed: {error}")

        total_time_ms = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
        if errors:
            if job.status != IndexStatus.FAILED:
                self.job_manager.fail_job(job.id, "; ".join(errors))
            final_status = IndexStatus.FAILED
        else:
            self.job_manager.transition(job.id, IndexStatus.COMPLETED)
            final_status = IndexStatus.COMPLETED

        return IndexingResult(
            job_id=job.id,
            document_id=chunks[0].document_id,
            status=final_status,
            chunks_indexed=len(chunks),
            vector_index_time_ms=vector_time_ms,
            lexical_index_time_ms=lexical_time_ms,
            total_time_ms=total_time_ms,
            errors=errors,
        )

    async def _prepare_embedding_texts(
        self,
        chunks: list[Chunk],
        document: Document | None,
    ) -> tuple[list[str], dict[str, object]]:
        """Return the embedding texts and contextual metadata for the current batch."""
        if (
            document is None
            or self.contextual_enricher is None
            or self.feature_flags is None
            or not self.feature_flags.is_enabled("contextual_indexing")
        ):
            return [chunk.content for chunk in chunks], {}

        contextual_chunks = await self.contextual_enricher.enrich(chunks, document)
        return (
            [chunk.contextual_content for chunk in contextual_chunks],
            {chunk.chunk_id: chunk for chunk in contextual_chunks},
        )

    def _maybe_apply_vector_compression(self, embeddings: list[list[float]]) -> list[list[float]]:
        """Apply benchmark-gated vector compression to the indexing path."""
        if not embeddings or self.compression_quantizer is None or self.feature_flags is None:
            return embeddings

        vectors = np.asarray(embeddings, dtype=np.float32)
        self._update_compression_benchmark(vectors)
        if not self._compression_enabled():
            return embeddings

        self._fit_quantizer(vectors)
        restored = self._quantize_and_restore(vectors).astype(np.float32)
        if self.compression_state_path is not None and hasattr(self.compression_quantizer, "save"):
            self.compression_quantizer.save(self.compression_state_path)
        return restored.tolist()

    def _update_compression_benchmark(self, vectors: np.ndarray) -> None:
        """Benchmark compression on the live indexing batch to unlock the feature gate."""
        if len(vectors) < 2 or self.compression_quantizer is None:
            return

        self._fit_quantizer(vectors)
        query_count = min(5, len(vectors))
        top_k = min(10, len(vectors))
        queries = vectors[:query_count].copy()
        ground_truth: list[list[int]] = []
        for query in queries:
            distances = np.linalg.norm(vectors - query, axis=1)
            ground_truth.append(list(np.argsort(distances)[:top_k]))

        stats = CompressionBenchmark(vectors=vectors, queries=queries, ground_truth=ground_truth).evaluate(
            self.compression_quantizer
        )
        self.feature_flags.update_benchmark(
            "vector_compression",
            BenchmarkResult(
                feature_name="vector_compression",
                baseline_score=1.0,
                feature_score=stats.compression_ratio,
                improvement_percent=(stats.compression_ratio - 1.0) * 100.0,
                passed_gate=stats.recall_at_10 >= self.compression_min_recall,
            ),
        )

    def _compression_enabled(self) -> bool:
        """Return whether the live indexing path should use compressed vectors."""
        return self.feature_flags is not None and self.feature_flags.is_enabled("vector_compression")

    def _fit_quantizer(self, vectors: np.ndarray) -> None:
        """Ensure the configured quantizer has fitted state."""
        if self.compression_quantizer is None:
            return
        if hasattr(self.compression_quantizer, "is_fitted") and self.compression_quantizer.is_fitted:
            return
        self.compression_quantizer.fit(vectors)

    def _quantize_and_restore(self, vectors: np.ndarray) -> np.ndarray:
        """Round-trip vectors through the configured compression codec."""
        if self.compression_quantizer is None:
            return vectors
        if hasattr(self.compression_quantizer, "quantize") and hasattr(self.compression_quantizer, "dequantize"):
            quantized = self.compression_quantizer.quantize(vectors)
            return self.compression_quantizer.dequantize(quantized)
        if hasattr(self.compression_quantizer, "encode") and hasattr(self.compression_quantizer, "decode"):
            encoded = self.compression_quantizer.encode(vectors)
            return self.compression_quantizer.decode(encoded)
        return vectors
