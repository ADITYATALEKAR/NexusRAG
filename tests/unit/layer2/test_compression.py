"""Unit tests for Phase 6 vector compression."""

from __future__ import annotations

import numpy as np

from src.layer2_domain.compression.benchmark import CompressionBenchmark
from src.layer2_domain.compression.quantizer import ProductQuantizer, ScalarQuantizer


def test_scalar_quantizer_achieves_four_x_compression() -> None:
    """Scalar quantization should compress float32 vectors down to uint8 values."""
    rng = np.random.default_rng(42)
    vectors = rng.normal(size=(64, 16)).astype(np.float32)
    quantizer = ScalarQuantizer()

    quantizer.fit(vectors)
    compressed = quantizer.quantize(vectors)
    restored = quantizer.dequantize(compressed)

    assert compressed.dtype == np.uint8
    assert vectors.nbytes / compressed.nbytes == 4.0
    assert restored.shape == vectors.shape


def test_scalar_quantization_benchmark_keeps_high_recall() -> None:
    """Scalar quantization should preserve recall within the Phase 6 gate."""
    vectors = np.stack(
        [np.linspace(0.0, 1.0, 16, dtype=np.float32) + (index * 10.0) for index in range(32)]
    ).astype(np.float32)
    queries = vectors[:5].copy()
    ground_truth: list[list[int]] = []
    for query in queries:
        distances = np.linalg.norm(vectors - query, axis=1)
        ground_truth.append(list(np.argsort(distances)[:10]))

    stats = CompressionBenchmark(vectors=vectors, queries=queries, ground_truth=ground_truth).evaluate(
        ScalarQuantizer()
    )

    assert stats.compression_ratio >= 4.0
    assert stats.recall_at_10 >= 0.98


def test_product_quantizer_encode_decode_shapes() -> None:
    """Product quantization should encode and decode vectors with stable shapes."""
    rng = np.random.default_rng(7)
    vectors = rng.normal(size=(32, 16)).astype(np.float32)
    quantizer = ProductQuantizer(num_subvectors=4, num_centroids=4)

    quantizer.fit(vectors)
    codes = quantizer.encode(vectors)
    decoded = quantizer.decode(codes)

    assert codes.shape == (32, 4)
    assert decoded.shape == vectors.shape
