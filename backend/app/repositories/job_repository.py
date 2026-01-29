import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.candidate import Candidate
from app.models.job import Job, JobStatus
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    """Repository for job operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Job, db)

    async def get_by_id(self, job_id: str) -> Job | None:
        """Get a job by ID."""
        stmt = select(Job).where(Job.job_id == job_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_with_candidate_count(
        self, limit: int = 100, offset: int = 0
    ) -> list[tuple[Job, int]]:
        """Get all jobs with their candidate counts."""
        stmt = (
            select(Job, func.count(Candidate.candidate_id).label("candidate_count"))
            .outerjoin(Candidate, Job.job_id == Candidate.job_id)
            .group_by(Job.job_id)
            .order_by(Job.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def create_job(self, title: str, job_text_raw: str, requirements_json: dict | None = None) -> Job:
        """Create a new job."""
        job = Job(
            job_id=str(uuid.uuid4()),
            title=title,
            job_text_raw=job_text_raw,
            requirements_json=requirements_json,
        )
        return await self.create(job)

    async def update_job(
        self,
        job: Job,
        title: str | None = None,
        job_text_raw: str | None = None,
        requirements_json: dict | None = None,
    ) -> Job:
        """Update a job."""
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if job_text_raw is not None:
            update_data["job_text_raw"] = job_text_raw
        if requirements_json is not None:
            update_data["requirements_json"] = requirements_json
        return await self.update(job, update_data)

    async def update_status(self, job: Job, status: JobStatus) -> Job:
        """Update job status."""
        return await self.update(job, {"status": status})
