"""Checksum helpers for ingestion."""

from __future__ import annotations

import hashlib


def compute_checksum(file_path: str, algorithm: str = "sha256") -> str:
    """Compute a checksum for a file on disk."""
    hash_func = hashlib.new(algorithm)
    with open(file_path, "rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(8192), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def compute_content_hash(content: bytes, algorithm: str = "sha256") -> str:
    """Compute a checksum for an in-memory payload."""
    return hashlib.new(algorithm, content).hexdigest()
