"""Pydantic schemas for cross-layer contracts."""

from src.layer1_contracts.schemas.answer import Answer, AnswerMetadata, AnswerStatus, Citation
from src.layer1_contracts.schemas.chunk import Chunk, ChunkLocation, ChunkMetadata
from src.layer1_contracts.schemas.chunking import (
    ChunkingConfig,
    ChunkingRequest,
    ChunkingResult,
    ChunkingStrategy,
)
from src.layer1_contracts.schemas.compression import CompressionMethod, CompressionStats
from src.layer1_contracts.schemas.contextual import ContextualChunk, DocumentContext
from src.layer1_contracts.schemas.document import Document, DocumentMetadata, DocumentStatus, DocumentType
from src.layer1_contracts.schemas.feature_flags import BenchmarkResult, FeatureFlag, FeatureStatus
from src.layer1_contracts.schemas.graph import EdgeType, GraphEdge, GraphNode, GraphQuery, NodeType
from src.layer1_contracts.schemas.embedding import EmbeddingRequest, EmbeddingResult
from src.layer1_contracts.schemas.decomposition import AggregatedAnswer, DecompositionPlan, SubQuery, SubQueryResult
from src.layer1_contracts.schemas.evidence import (
    EvidenceAssemblyResult,
    EvidenceBundle,
    EvidenceConfig,
    EvidenceItem,
    EvidenceSelectionStrategy,
)
from src.layer1_contracts.schemas.evaluation import (
    EvalDataset,
    EvalDatasetItem,
    EvalRunResult,
    GenerationMetricsResult,
    MetricType,
    RegressionResult,
    RetrievalMetricsResult,
)
from src.layer1_contracts.schemas.generation import (
    AbstentionReason,
    GenerationConfig,
    GenerationRequest,
    GenerationTrace,
)
from src.layer1_contracts.schemas.health import ComponentHealth, HealthStatus, ProviderHealth, SystemHealth
from src.layer1_contracts.schemas.ingestion import FileMetadata, IngestionRequest, IngestionResult, IngestionStatus
from src.layer1_contracts.schemas.indexing import IndexJob, IndexingResult, IndexState, IndexStatus
from src.layer1_contracts.schemas.llm import (
    LLMConfig,
    LLMRequest,
    LLMResponse,
    LLMUsage,
    Message,
    MessageRole,
)
from src.layer1_contracts.schemas.normalization import ChunkPrecursor, NormalizedDocument, NormalizedSection
from src.layer1_contracts.schemas.observability import CostRecord, LogEntry, LogLevel, MetricPoint, SpanContext
from src.layer1_contracts.schemas.parsing import ParseResult, ParsedPage, ParsedSection
from src.layer1_contracts.schemas.query import Query, QueryConfig, QueryFilters, QueryType
from src.layer1_contracts.schemas.query_understanding import (
    DetectedEntity,
    QueryAnalysis,
    QueryComplexity,
    QueryIntent,
)
from src.layer1_contracts.schemas.rerank import RerankRequest, RerankResult
from src.layer1_contracts.schemas.retrieval import (
    HybridRetrievalResult,
    RetrievalCandidate,
    RetrievalDiagnostics,
    RetrievalResult,
    RetrievalScores,
    RetrievalStageResult,
)
from src.layer1_contracts.schemas.retrieval_config import (
    FilterConfig,
    FusionMethod,
    RetrievalConfig,
    RetrievalMode,
)
from src.layer1_contracts.schemas.routing import Route, RouteType, RoutingDecision, RoutingDiagnostics
from src.layer1_contracts.schemas.structured import GeneratedSQL, StructuredQuery, StructuredQueryType, StructuredResult
from src.layer1_contracts.schemas.security import (
    AuditEvent,
    SecurityDecision,
    SecurityDecisionType,
    ThreatCategory,
)

__all__ = [
    "Answer",
    "AnswerMetadata",
    "AnswerStatus",
    "AggregatedAnswer",
    "AuditEvent",
    "BenchmarkResult",
    "Chunk",
    "ChunkLocation",
    "ChunkMetadata",
    "ChunkingConfig",
    "ChunkingRequest",
    "ChunkingResult",
    "ChunkingStrategy",
    "Citation",
    "CompressionMethod",
    "CompressionStats",
    "ComponentHealth",
    "ContextualChunk",
    "DecompositionPlan",
    "DetectedEntity",
    "Document",
    "DocumentContext",
    "DocumentMetadata",
    "DocumentStatus",
    "DocumentType",
    "EdgeType",
    "EmbeddingRequest",
    "EmbeddingResult",
    "EvalDataset",
    "EvalDatasetItem",
    "EvalRunResult",
    "EvidenceAssemblyResult",
    "EvidenceBundle",
    "EvidenceConfig",
    "EvidenceItem",
    "EvidenceSelectionStrategy",
    "FileMetadata",
    "FeatureFlag",
    "FeatureStatus",
    "GenerationMetricsResult",
    "GenerationConfig",
    "GenerationRequest",
    "GenerationTrace",
    "GraphEdge",
    "GraphNode",
    "GraphQuery",
    "HealthStatus",
    "IndexJob",
    "IndexingResult",
    "IndexState",
    "IndexStatus",
    "IngestionRequest",
    "IngestionResult",
    "IngestionStatus",
    "LLMConfig",
    "LLMRequest",
    "LLMResponse",
    "LLMUsage",
    "CostRecord",
    "LogEntry",
    "LogLevel",
    "Message",
    "MessageRole",
    "MetricPoint",
    "MetricType",
    "ChunkPrecursor",
    "NormalizedDocument",
    "NormalizedSection",
    "NodeType",
    "ParseResult",
    "ParsedPage",
    "ParsedSection",
    "ProviderHealth",
    "Query",
    "QueryAnalysis",
    "QueryComplexity",
    "QueryConfig",
    "QueryFilters",
    "QueryIntent",
    "QueryType",
    "RerankRequest",
    "RerankResult",
    "Route",
    "RoutingDecision",
    "RoutingDiagnostics",
    "RouteType",
    "FilterConfig",
    "FusionMethod",
    "GeneratedSQL",
    "HybridRetrievalResult",
    "RetrievalConfig",
    "RetrievalCandidate",
    "RetrievalDiagnostics",
    "RetrievalMetricsResult",
    "RetrievalMode",
    "RetrievalResult",
    "RetrievalScores",
    "RetrievalStageResult",
    "RegressionResult",
    "SecurityDecision",
    "SecurityDecisionType",
    "SpanContext",
    "StructuredQuery",
    "StructuredQueryType",
    "StructuredResult",
    "SubQuery",
    "SubQueryResult",
    "SystemHealth",
    "ThreatCategory",
    "AbstentionReason",
]
