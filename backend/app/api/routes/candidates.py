from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.candidate import CandidateStatus
from app.schemas.candidate import CandidateCreate, CandidateDetail, CandidateListItem, CandidateUpdate
from app.services.candidate_service import CandidateService

router = APIRouter()


@router.post(
    "/jobs/{job_id}/candidates",
    response_model=CandidateDetail,
    status_code=status.HTTP_201_CREATED,
)
async def create_candidate(
    job_id: str,
    data: CandidateCreate,
    db: AsyncSession = Depends(get_db),
) -> CandidateDetail:
    """Create a new candidate for a job."""
    service = CandidateService(db)
    return await service.create_candidate(job_id, data)


@router.get("/jobs/{job_id}/candidates", response_model=list[CandidateListItem])
async def list_candidates(
    job_id: str,
    limit: int = 100,
    offset: int = 0,
    sort_by_score: bool = True,
    db: AsyncSession = Depends(get_db),
) -> list[CandidateListItem]:
    """List candidates for a job, optionally ranked by score."""
    service = CandidateService(db)
    return await service.list_candidates(job_id, limit, offset, sort_by_score)


@router.get("/candidates/{candidate_id}", response_model=CandidateDetail)
async def get_candidate(
    candidate_id: str,
    db: AsyncSession = Depends(get_db),
) -> CandidateDetail:
    """Get candidate details including scores and explanations."""
    service = CandidateService(db)
    return await service.get_candidate(candidate_id)


@router.patch("/candidates/{candidate_id}", response_model=CandidateDetail)
async def update_candidate(
    candidate_id: str,
    data: CandidateUpdate,
    db: AsyncSession = Depends(get_db),
) -> CandidateDetail:
    """Update candidate information (status, display_name)."""
    service = CandidateService(db)
    if data.status is not None:
        return await service.update_status(candidate_id, data.status)
    # If no status update, just get and return the candidate
    return await service.get_candidate(candidate_id)
