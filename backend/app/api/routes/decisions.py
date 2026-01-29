from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.decision import DecisionCreate, DecisionResponse
from app.services.decision_service import DecisionService

router = APIRouter()


@router.post(
    "/candidates/{candidate_id}/decision",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_decision(
    candidate_id: str,
    data: DecisionCreate,
    db: AsyncSession = Depends(get_db),
) -> DecisionResponse:
    """Record a decision for a candidate."""
    service = DecisionService(db)
    return await service.create_decision(candidate_id, data)


@router.get("/candidates/{candidate_id}/decisions", response_model=list[DecisionResponse])
async def list_decisions(
    candidate_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[DecisionResponse]:
    """Get all decisions for a candidate."""
    service = DecisionService(db)
    return await service.get_decisions(candidate_id)
