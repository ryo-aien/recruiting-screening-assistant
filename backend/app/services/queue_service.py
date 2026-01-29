from sqlalchemy.ext.asyncio import AsyncSession

from app.models.jobs_queue import JobsQueue, JobType, QueueStatus
from app.repositories.queue_repository import QueueRepository


class QueueService:
    """Service for job queue operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.queue_repo = QueueRepository(db)

    async def enqueue_job(self, candidate_id: str, job_type: JobType) -> JobsQueue:
        """Add a job to the queue."""
        return await self.queue_repo.create_job(candidate_id, job_type)

    async def enqueue_next_job(self, candidate_id: str, current_job_type: JobType) -> JobsQueue | None:
        """Enqueue the next job in the pipeline after current job completes."""
        next_job_map = {
            JobType.TEXT_EXTRACT: JobType.LLM_EXTRACT,
            JobType.LLM_EXTRACT: JobType.EMBED,
            JobType.EMBED: JobType.SCORE,
            JobType.SCORE: JobType.EXPLAIN,
        }

        next_type = next_job_map.get(current_job_type)
        if next_type:
            return await self.queue_repo.create_job(candidate_id, next_type)
        return None

    async def get_next_job(self, job_type: JobType | None = None) -> JobsQueue | None:
        """Get the next job ready for processing."""
        return await self.queue_repo.get_next_ready_job(job_type)

    async def mark_running(self, job: JobsQueue) -> JobsQueue:
        """Mark a job as running."""
        return await self.queue_repo.mark_running(job)

    async def mark_done(self, job: JobsQueue) -> JobsQueue:
        """Mark a job as done."""
        return await self.queue_repo.mark_done(job)

    async def mark_failed(self, job: JobsQueue, error: str) -> JobsQueue:
        """Mark a job as failed."""
        return await self.queue_repo.mark_failed(job, error)

    async def retry_job(self, job: JobsQueue) -> JobsQueue:
        """Reset a job for retry."""
        return await self.queue_repo.retry_job(job)

    async def get_failed_jobs(self, limit: int = 100) -> list[JobsQueue]:
        """Get failed jobs for review."""
        return await self.queue_repo.get_failed_jobs(limit)
