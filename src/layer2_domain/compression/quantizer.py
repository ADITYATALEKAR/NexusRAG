"""Vector compression utilities."""

from __future__ import annotations

from pathlib import Path

import numpy as np


class ScalarQuantizer:
    """8-bit scalar quantization for roughly 4x compression."""

    def __init__(self) -> None:
        self.min_vals: np.ndarray | None = None
        self.max_vals: np.ndarray | None = None
        self.scale: np.ndarray | None = None

    @property
    def is_fitted(self) -> bool:
        """Return whether quantization parameters are available."""
        return self.min_vals is not None and self.max_vals is not None and self.scale is not None

    def fit(self, vectors: np.ndarray) -> None:
        """Fit per-dimension min/max ranges for quantization."""
        vectors = np.asarray(vectors, dtype=np.float32)
        self.min_vals = vectors.min(axis=0)
        self.max_vals = vectors.max(axis=0)
        self.scale = (self.max_vals - self.min_vals) / 255.0
        self.scale[self.scale == 0] = 1.0

    def quantize(self, vectors: np.ndarray) -> np.ndarray:
        """Quantize vectors to 8-bit unsigned integer values."""
        if self.min_vals is None or self.scale is None:
            raise ValueError("ScalarQuantizer must be fit before quantize")
        vectors = np.asarray(vectors, dtype=np.float32)
        return np.clip((vectors - self.min_vals) / self.scale, 0, 255).astype(np.uint8)

    def dequantize(self, quantized: np.ndarray) -> np.ndarray:
        """Reconstruct approximate float vectors from quantized values."""
        if self.min_vals is None or self.scale is None:
            raise ValueError("ScalarQuantizer must be fit before dequantize")
        return quantized.astype(np.float32) * self.scale + self.min_vals

    def save(self, path: str | Path) -> None:
        """Persist quantization parameters for reuse at retrieval time."""
        if not self.is_fitted:
            raise ValueError("ScalarQuantizer must be fit before save")
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        np.savez(
            target,
            min_vals=self.min_vals,
            max_vals=self.max_vals,
            scale=self.scale,
        )

    @classmethod
    def load(cls, path: str | Path) -> "ScalarQuantizer":
        """Load persisted quantization parameters."""
        payload = np.load(Path(path))
        quantizer = cls()
        quantizer.min_vals = payload["min_vals"].astype(np.float32)
        quantizer.max_vals = payload["max_vals"].astype(np.float32)
        quantizer.scale = payload["scale"].astype(np.float32)
        return quantizer


class ProductQuantizer:
    """Product quantization using independent KMeans codebooks per subvector."""

    def __init__(self, num_subvectors: int = 8, num_centroids: int = 256) -> None:
        self.num_subvectors = num_subvectors
        self.num_centroids = num_centroids
        self.centroids: list[np.ndarray] = []

    @property
    def is_fitted(self) -> bool:
        """Return whether codebooks are available."""
        return bool(self.centroids)

    def fit(self, vectors: np.ndarray) -> None:
        """Fit KMeans codebooks for each subvector slice."""
        from sklearn.cluster import KMeans

        vectors = np.asarray(vectors, dtype=np.float32)
        if vectors.shape[1] % self.num_subvectors != 0:
            raise ValueError("Vector dimensionality must be divisible by num_subvectors")
        subvector_dim = vectors.shape[1] // self.num_subvectors
        self.centroids = []
        for index in range(self.num_subvectors):
            subspace = vectors[:, index * subvector_dim : (index + 1) * subvector_dim]
            model = KMeans(n_clusters=self.num_centroids, n_init=10, random_state=42)
            model.fit(subspace)
            self.centroids.append(model.cluster_centers_.astype(np.float32))

    def encode(self, vectors: np.ndarray) -> np.ndarray:
        """Encode vectors into compact centroid indices."""
        vectors = np.asarray(vectors, dtype=np.float32)
        if not self.centroids:
            raise ValueError("ProductQuantizer must be fit before encode")
        subvector_dim = vectors.shape[1] // self.num_subvectors
        codes = []
        for index, centroids in enumerate(self.centroids):
            subspace = vectors[:, index * subvector_dim : (index + 1) * subvector_dim]
            distances = np.linalg.norm(subspace[:, :, None] - centroids.T[None, :, :], axis=1)
            codes.append(distances.argmin(axis=1))
        return np.column_stack(codes).astype(np.uint8)

    def decode(self, codes: np.ndarray) -> np.ndarray:
        """Decode centroid indices back into approximate float vectors."""
        if not self.centroids:
            raise ValueError("ProductQuantizer must be fit before decode")
        reconstructions = [centroids[codes[:, index]] for index, centroids in enumerate(self.centroids)]
        return np.hstack(reconstructions).astype(np.float32)

    def save(self, path: str | Path) -> None:
        """Persist centroid codebooks for reuse."""
        if not self.is_fitted:
            raise ValueError("ProductQuantizer must be fit before save")
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        np.savez(
            target,
            num_subvectors=np.asarray([self.num_subvectors], dtype=np.int32),
            num_centroids=np.asarray([self.num_centroids], dtype=np.int32),
            centroids=np.asarray(self.centroids, dtype=object),
        )

    @classmethod
    def load(cls, path: str | Path) -> "ProductQuantizer":
        """Load persisted centroid codebooks."""
        payload = np.load(Path(path), allow_pickle=True)
        quantizer = cls(
            num_subvectors=int(payload["num_subvectors"][0]),
            num_centroids=int(payload["num_centroids"][0]),
        )
        quantizer.centroids = [centroid.astype(np.float32) for centroid in payload["centroids"].tolist()]
        return quantizer
