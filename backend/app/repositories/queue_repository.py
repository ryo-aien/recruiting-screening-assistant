import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.jobs_queue import JobsQueue, JobType, QueueStatus
from app.repositories.base import BaseRepository


class QueueRepository(BaseRepository[JobsQueue]):
    """Repository for job queue operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(JobsQueue, db)

    async def get_by_id(self, queue_id: str) -> JobsQueue | None:
        """Get a queue job by ID."""
        stmt = select(JobsQueue).where(JobsQueue.queue_id == queue_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_next_ready_job(self, job_type: JobType | None = None) -> JobsQueue | None:
        """Get the next ready job for processing (FIFO)."""
        stmt = (
            select(JobsQueue)
            .where(JobsQueue.status == QueueStatus.READY)
        )
        if job_type:
            stmt = stmt.where(JobsQueue.job_type == job_type)
        stmt = stmt.order_by(JobsQueue.created_at.asc()).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_ready_jobs(
        self, job_type: JobType | None = None, limit: int = 10
    ) -> list[JobsQueue]:
        """Get ready jobs for processing."""
        stmt = select(JobsQueue).where(JobsQueue.status == QueueStatus.READY)
        if job_type:
            stmt = stmt.where(JobsQueue.job_type == job_type)
        stmt = stmt.order_by(JobsQueue.created_at.asc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_candidate_and_type(
        self, candidate_id: str, job_type: JobType
    ) -> JobsQueue | None:
        """Get a queue job by candidate ID and type."""
        stmt = (
            select(JobsQueue)
            .where(JobsQueue.candidate_id == candidate_id)
            .where(JobsQueue.job_type == job_type)
            .order_by(JobsQueue.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_job(self, candidate_id: str, job_type: JobType) -> JobsQueue:
        """Create a new queue job."""
        job = JobsQueue(
            queue_id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            job_type=job_type,
            status=QueueStatus.READY,
            attempts=0,
        )
        return await self.create(job)

    async def mark_running(self, job: JobsQueue) -> JobsQueue:
        """Mark a job as running."""
        return await self.update(
            job,
            {
                "status": QueueStatus.RUNNING,
                "attempts": job.attempts + 1,
            },
        )

    async def mark_done(self, job: JobsQueue) -> JobsQueue:
        """Mark a job as done."""
        return await self.update(job, {"status": QueueStatus.DONE})

    async def mark_failed(self, job: JobsQueue, error: str) -> JobsQueue:
        """Mark a job as failed."""
        return await self.update(
            job,
            {
                "status": QueueStatus.FAILED,
                "last_error": error,
            },
        )

    async def retry_job(self, job: JobsQueue) -> JobsQueue:
        """Reset a job to ready status for retry."""
        return await self.update(job, {"status": QueueStatus.READY})

    async def get_failed_jobs(self, limit: int = 100) -> list[JobsQueue]:
        """Get failed jobs."""
        stmt = (
            select(JobsQueue)
            .where(JobsQueue.status == QueueStatus.FAILED)
            .order_by(JobsQueue.updated_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
