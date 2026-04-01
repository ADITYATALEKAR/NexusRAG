"""Benchmark helpers for vector compression."""

from __future__ import annotations

import numpy as np

from src.layer1_contracts.schemas.compression import CompressionStats


class CompressionBenchmark:
    """Evaluate compression quality and storage savings."""

    def __init__(self, vectors: np.ndarray, queries: np.ndarray, ground_truth: list[list[int]]) -> None:
        self.vectors = np.asarray(vectors, dtype=np.float32)
        self.queries = np.asarray(queries, dtype=np.float32)
        self.ground_truth = ground_truth

    def evaluate(self, quantizer) -> CompressionStats:
        """Fit, compress, decompress, and score a quantizer."""
        quantizer.fit(self.vectors)
        if hasattr(quantizer, "quantize"):
            compressed = quantizer.quantize(self.vectors)
            decompressed = quantizer.dequantize(compressed)
        else:
            compressed = quantizer.encode(self.vectors)
            decompressed = quantizer.decode(compressed)

        recalls: list[float] = []
        k = max(1, min(10, len(self.vectors)))
        for index, query in enumerate(self.queries):
            distances = np.linalg.norm(decompressed - query, axis=1)
            approximate_top_k = np.argsort(distances)[:k]
            exact_top_k = set(self.ground_truth[index][:k])
            recalls.append(len(set(approximate_top_k) & exact_top_k) / float(k))

        return CompressionStats(
            compression_ratio=float(self.vectors.nbytes / compressed.nbytes),
            recall_at_10=float(sum(recalls) / len(recalls)),
        )
