"""Graph retrieval contracts."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class NodeType(str, Enum):
    """Supported graph node types."""

    DOCUMENT = "document"
    CHUNK = "chunk"
    ENTITY = "entity"


class EdgeType(str, Enum):
    """Supported graph edge types."""

    CONTAINS = "contains"
    REFERENCES = "references"
    RELATED_TO = "related_to"
    FOLLOWS = "follows"


class GraphNode(BaseModel):
    """Serializable node description returned by traversal."""

    model_config = ConfigDict(extra="forbid")

    id: str
    node_type: NodeType
    content: str | None = None


class GraphEdge(BaseModel):
    """Serializable graph edge contract."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0


class GraphQuery(BaseModel):
    """Traversal query for graph expansion."""

    model_config = ConfigDict(extra="forbid")

    seed_nodes: list[str] = Field(default_factory=list)
    max_hops: int = Field(default=2, ge=0)
    max_nodes: int = Field(default=50, ge=1)
