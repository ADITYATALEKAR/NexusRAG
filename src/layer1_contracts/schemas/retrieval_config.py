"""Retrieval configuration contracts."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FusionMethod(str, Enum):
    """Supported fusion methods for hybrid retrieval."""

    RRF = "rrf"
    WEIGHTED = "weighted"
    MAX_SCORE = "max_score"


class RetrievalMode(str, Enum):
    """Available retrieval execution modes."""

    DENSE_ONLY = "dense_only"
    LEXICAL_ONLY = "lexical_only"
    HYBRID = "hybrid"


class RetrievalConfig(BaseModel):
    """Configuration for one retrieval execution."""

    model_config = ConfigDict(extra="forbid")

    mode: RetrievalMode = RetrievalMode.HYBRID
    dense_top_k: int = Field(default=50, ge=1, le=500)
    lexical_top_k: int = Field(default=50, ge=1, le=500)
    fusion_top_k: int = Field(default=25, ge=1, le=200)
    final_top_k: int = Field(default=10, ge=1, le=100)
    fusion_method: FusionMethod = FusionMethod.RRF
    rrf_k: int = Field(default=60, ge=1)
    dense_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    lexical_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    apply_metadata_filter: bool = True
    apply_freshness_boost: bool = True
    freshness_decay_days: int = Field(default=30, ge=1)
    min_score_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    rerank_enabled: bool = True
    rerank_top_k: int = Field(default=25, ge=1, le=100)

    @model_validator(mode="after")
    def validate_rerank_bounds(self) -> "RetrievalConfig":
        """Ensure rerank bounds remain coherent."""
        if self.rerank_enabled and self.rerank_top_k < self.final_top_k:
            raise ValueError("rerank_top_k must be >= final_top_k when reranking is enabled")
        return self


class FilterConfig(BaseModel):
    """Filter configuration for retrieval stages."""

    model_config = ConfigDict(extra="forbid")

    document_ids: list[str] | None = None
    document_types: list[str] | None = None
    tags: list[str] | None = None
    date_from: str | None = None
    date_to: str | None = None
    min_trust_score: float | None = Field(default=None, ge=0.0, le=1.0)
    exclude_chunk_ids: list[str] | None = None
