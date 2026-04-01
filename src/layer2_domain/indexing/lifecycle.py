"""Index lifecycle state machine."""

from __future__ import annotations

from datetime import datetime, timezone

from src.layer1_contracts.schemas.indexing import IndexJob, IndexStatus


class IndexLifecycle:
    """Validate and apply index job state transitions."""

    ALLOWED_TRANSITIONS: dict[IndexStatus, set[IndexStatus]] = {
        IndexStatus.PENDING: {IndexStatus.EMBEDDING, IndexStatus.FAILED, IndexStatus.STALE},
        IndexStatus.EMBEDDING: {IndexStatus.VECTOR_INDEXING, IndexStatus.FAILED, IndexStatus.STALE},
        IndexStatus.VECTOR_INDEXING: {IndexStatus.LEXICAL_INDEXING, IndexStatus.FAILED, IndexStatus.STALE},
        IndexStatus.LEXICAL_INDEXING: {IndexStatus.COMPLETED, IndexStatus.FAILED, IndexStatus.STALE},
        IndexStatus.COMPLETED: {IndexStatus.STALE},
        IndexStatus.FAILED: {IndexStatus.PENDING, IndexStatus.STALE},
        IndexStatus.STALE: {IndexStatus.PENDING},
    }

    def can_transition(self, current: IndexStatus, new: IndexStatus) -> bool:
        """Return whether the new state is legal from the current state."""
        return new in self.ALLOWED_TRANSITIONS.get(current, set())

    def transition(self, job: IndexJob, new_status: IndexStatus) -> IndexJob:
        """Apply a validated transition to an index job."""
        if not self.can_transition(job.status, new_status):
            raise ValueError(f"Invalid index transition: {job.status} -> {new_status}")

        job.status = new_status
        now = datetime.now(timezone.utc)
        if new_status == IndexStatus.EMBEDDING and job.started_at is None:
            job.started_at = now
        if new_status in {IndexStatus.COMPLETED, IndexStatus.FAILED}:
            job.completed_at = now
        return job
