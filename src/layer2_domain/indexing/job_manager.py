"""Index job orchestration."""

from __future__ import annotations

from datetime import datetime, timezone

from src.layer1_contracts.schemas.indexing import IndexJob, IndexStatus
from src.layer2_domain.indexing.lifecycle import IndexLifecycle


class IndexJobManager:
    """Manage in-memory index jobs for orchestration and observability."""

    def __init__(self, lifecycle: IndexLifecycle | None = None) -> None:
        self.lifecycle = lifecycle or IndexLifecycle()
        self._jobs: dict[str, IndexJob] = {}

    def create_job(
        self,
        document_id: str,
        chunk_ids: list[str],
        vector_store_id: str | None = None,
        lexical_store_id: str | None = None,
    ) -> IndexJob:
        """Create and register a new index job."""
        job_id = f"idx-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        job = IndexJob(
            id=job_id,
            document_id=document_id,
            chunk_ids=list(chunk_ids),
            vector_store_id=vector_store_id,
            lexical_store_id=lexical_store_id,
        )
        self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> IndexJob | None:
        """Return a job by id if present."""
        return self._jobs.get(job_id)

    def transition(self, job_id: str, status: IndexStatus) -> IndexJob:
        """Transition a job to a new state."""
        job = self._require_job(job_id)
        return self.lifecycle.transition(job, status)

    def fail_job(self, job_id: str, error: str) -> IndexJob:
        """Mark a job as failed and attach an error message."""
        job = self.transition(job_id, IndexStatus.FAILED)
        job.error = error
        return job

    def list_jobs(self) -> list[IndexJob]:
        """Return all tracked jobs."""
        return list(self._jobs.values())

    def _require_job(self, job_id: str) -> IndexJob:
        job = self.get(job_id)
        if job is None:
            raise KeyError(f"Unknown index job: {job_id}")
        return job
