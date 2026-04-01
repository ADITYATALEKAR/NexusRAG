"""Vector compression contracts."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class CompressionMethod(str, Enum):
    """Supported vector compression methods."""

    NONE = "none"
    SCALAR_QUANTIZATION = "scalar"
    PRODUCT_QUANTIZATION = "pq"


class CompressionStats(BaseModel):
    """Compression efficiency and retrieval-quality measurements."""

    model_config = ConfigDict(extra="forbid")

    compression_ratio: float = Field(gt=0.0)
    recall_at_10: float = Field(ge=0.0, le=1.0)
