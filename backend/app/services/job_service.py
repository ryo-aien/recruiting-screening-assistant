from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.job import Job
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobCreate, JobDetail, JobListItem, JobUpdate


class JobService:
    """Service for job operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_repo = JobRepository(db)

    async def create_job(self, data: JobCreate) -> JobDetail:
        """Create a new job."""
        job = await self.job_repo.create_job(
            title=data.title,
            job_text_raw=data.job_text_raw,
            requirements_json=data.requirements_json,
        )
        return JobDetail.model_validate(job)

    async def get_job(self, job_id: str) -> JobDetail:
        """Get a job by ID."""
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundException(f"Job {job_id} not found")
        return JobDetail.model_validate(job)

    async def list_jobs(self, limit: int = 100, offset: int = 0) -> list[JobListItem]:
        """List all jobs with candidate counts."""
        jobs_with_counts = await self.job_repo.get_all_with_candidate_count(limit, offset)
        return [
            JobListItem(
                job_id=job.job_id,
                title=job.title,
                status=job.status,
                created_at=job.created_at,
                updated_at=job.updated_at,
                candidate_count=count,
            )
            for job, count in jobs_with_counts
        ]

    async def update_job(self, job_id: str, data: JobUpdate) -> JobDetail:
        """Update a job."""
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundException(f"Job {job_id} not found")

        # Update status if provided
        if data.status is not None:
            job = await self.job_repo.update_status(job, data.status)

        # Update other fields
        if data.title is not None or data.job_text_raw is not None or data.requirements_json is not None:
            job = await self.job_repo.update_job(
                job=job,
                title=data.title,
                job_text_raw=data.job_text_raw,
                requirements_json=data.requirements_json,
            )

        return JobDetail.model_validate(job)

    async def delete_job(self, job_id: str) -> bool:
        """Delete a job."""
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundException(f"Job {job_id} not found")
        return await self.job_repo.delete(job)
