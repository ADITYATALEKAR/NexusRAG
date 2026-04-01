"""Qdrant vector store adapter."""

from __future__ import annotations

import hashlib
from pathlib import Path

from qdrant_client import QdrantClient, models

from src.layer1_contracts.interfaces.vector_store import VectorStoreInterface


class QdrantAdapter(VectorStoreInterface):
    """Vector store adapter backed by Qdrant."""

    _LOCAL_CLIENTS: dict[str, QdrantClient] = {}

    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection: str = "chunks",
        dimensions: int = 384,
        api_key: str | None = None,
    ) -> None:
        self.collection = collection
        self.dimensions = dimensions
        self.client = self._build_client(url, api_key=api_key)
        self._ensure_collection()

    async def insert(
        self,
        ids: list[str],
        vectors: list[list[float]],
        metadata: list[dict] | None = None,
    ) -> int:
        """Insert vectors into the Qdrant collection."""
        points: list[models.PointStruct] = []
        for index, (chunk_id, vector) in enumerate(zip(ids, vectors)):
            payload = {"chunk_id": chunk_id, "_id": chunk_id}
            if metadata:
                payload.update(metadata[index])
            points.append(
                models.PointStruct(
                    id=self._point_id(chunk_id),
                    vector=vector,
                    payload=payload,
                )
            )

        self.client.upsert(collection_name=self.collection, points=points, wait=True)
        return len(points)

    async def upsert(
        self,
        ids: list[str],
        vectors: list[list[float]],
        metadata: list[dict] | None = None,
    ) -> int:
        """Insert or update vectors."""
        return await self.insert(ids, vectors, metadata)

    async def delete(self, ids: list[str]) -> int:
        """Delete vectors by chunk id."""
        for chunk_id in ids:
            self.client.delete(
                collection_name=self.collection,
                points_selector=models.FilterSelector(filter=self._id_filter(chunk_id)),
                wait=True,
            )
        return len(ids)

    async def search(
        self,
        query_vector: list[float],
        top_k: int = 10,
        filter: dict | None = None,
    ) -> list[tuple[str, float, dict | None]]:
        """Search the collection for similar vectors."""
        results = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            query_filter=self._payload_filter(filter),
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )
        return [(result.payload.get("_id", str(result.id)), result.score, result.payload) for result in results]

    async def fetch(self, ids: list[str]) -> list[tuple[str, list[float], dict | None]]:
        """Fetch vectors by chunk id."""
        results: list[tuple[str, list[float], dict | None]] = []
        for chunk_id in ids:
            points, _ = self.client.scroll(
                collection_name=self.collection,
                scroll_filter=self._id_filter(chunk_id),
                limit=1,
                with_payload=True,
                with_vectors=True,
            )
            if points:
                point = points[0]
                results.append((chunk_id, list(point.vector), point.payload))
        return results

    async def health_check(self) -> bool:
        """Return whether the Qdrant collection is reachable."""
        try:
            self.client.get_collection(self.collection)
            return True
        except Exception:  # noqa: BLE001
            return False

    async def collection_exists(self, name: str) -> bool:
        """Return whether a collection exists."""
        collections = self.client.get_collections().collections
        return any(collection.name == name for collection in collections)

    async def count(self) -> int:
        """Return the number of stored points."""
        info = self.client.get_collection(self.collection)
        return int(info.points_count or 0)

    def _build_client(self, url: str, api_key: str | None = None) -> QdrantClient:
        """Build a Qdrant client, supporting in-memory and local persistent modes."""
        if url in {"memory://", ":memory:"}:
            return QdrantClient(location=":memory:")
        if url.startswith("file://"):
            path = Path(url.removeprefix("file://"))
            path.mkdir(parents=True, exist_ok=True)
            return self._get_or_create_local_client(path)
        if "://" not in url:
            path = Path(url)
            path.mkdir(parents=True, exist_ok=True)
            return self._get_or_create_local_client(path)
        return QdrantClient(url=url, api_key=api_key)

    @classmethod
    def _get_or_create_local_client(cls, path: Path) -> QdrantClient:
        """Reuse local persistent clients per path to avoid file locking conflicts."""
        resolved = str(path.resolve())
        client = cls._LOCAL_CLIENTS.get(resolved)
        if client is None or getattr(getattr(client, "_client", None), "closed", False):
            client = QdrantClient(path=resolved)
            cls._LOCAL_CLIENTS[resolved] = client
        return client

    def _ensure_collection(self) -> None:
        """Create the collection if it does not already exist."""
        collections = self.client.get_collections().collections
        if not any(collection.name == self.collection for collection in collections):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=models.VectorParams(size=self.dimensions, distance=models.Distance.COSINE),
            )

    def _point_id(self, chunk_id: str) -> int:
        """Convert a string chunk id into a stable integer point id."""
        return int(hashlib.sha1(chunk_id.encode("utf-8")).hexdigest()[:16], 16)

    def _id_filter(self, chunk_id: str) -> models.Filter:
        """Build a filter for one chunk id."""
        return models.Filter(
            must=[models.FieldCondition(key="_id", match=models.MatchValue(value=chunk_id))]
        )

    def _payload_filter(self, filter_values: dict | None) -> models.Filter | None:
        """Convert a simple equality filter dict into a Qdrant filter."""
        if not filter_values:
            return None
        conditions = [
            models.FieldCondition(key=key, match=models.MatchValue(value=value))
            for key, value in filter_values.items()
        ]
        return models.Filter(must=conditions)
