from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.job import JobCreate, JobDetail, JobListItem, JobUpdate
from app.services.job_service import JobService

router = APIRouter()


@router.post("", response_model=JobDetail, status_code=status.HTTP_201_CREATED)
async def create_job(
    data: JobCreate,
    db: AsyncSession = Depends(get_db),
) -> JobDetail:
    """Create a new job posting."""
    service = JobService(db)
    return await service.create_job(data)


@router.get("", response_model=list[JobListItem])
async def list_jobs(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> list[JobListItem]:
    """List all job postings."""
    service = JobService(db)
    return await service.list_jobs(limit, offset)


@router.get("/{job_id}", response_model=JobDetail)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> JobDetail:
    """Get a job posting by ID."""
    service = JobService(db)
    return await service.get_job(job_id)


@router.patch("/{job_id}", response_model=JobDetail)
async def update_job(
    job_id: str,
    data: JobUpdate,
    db: AsyncSession = Depends(get_db),
) -> JobDetail:
    """Update a job posting."""
    service = JobService(db)
    return await service.update_job(job_id, data)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a job posting."""
    service = JobService(db)
    await service.delete_job(job_id)
