import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.candidate import Candidate, CandidateStatus
from app.models.decision import Decision
from app.models.document import Document
from app.models.explanation import Explanation
from app.models.extraction import Extraction
from app.models.score import Score
from app.repositories.base import BaseRepository


class CandidateRepository(BaseRepository[Candidate]):
    """Repository for candidate operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Candidate, db)

    async def get_by_id(self, candidate_id: str) -> Candidate | None:
        """Get a candidate by ID."""
        stmt = select(Candidate).where(Candidate.candidate_id == candidate_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_details(self, candidate_id: str) -> Candidate | None:
        """Get a candidate by ID with all related data."""
        stmt = (
            select(Candidate)
            .where(Candidate.candidate_id == candidate_id)
            .options(
                selectinload(Candidate.documents),
                selectinload(Candidate.extraction),
                selectinload(Candidate.score),
                selectinload(Candidate.explanation),
                selectinload(Candidate.decisions),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_job_id(
        self, job_id: str, limit: int = 100, offset: int = 0
    ) -> list[Candidate]:
        """Get all candidates for a job."""
        stmt = (
            select(Candidate)
            .where(Candidate.job_id == job_id)
            .options(
                selectinload(Candidate.score),
                selectinload(Candidate.explanation),
                selectinload(Candidate.decisions),
            )
            .order_by(Candidate.submitted_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_job_id_ranked(
        self, job_id: str, limit: int = 100, offset: int = 0
    ) -> list[Candidate]:
        """Get candidates for a job ranked by total_fit score."""
        from sqlalchemy import case

        # MySQL doesn't support NULLS LAST, so we use CASE to sort NULLs at the end
        stmt = (
            select(Candidate)
            .where(Candidate.job_id == job_id)
            .outerjoin(Score, Candidate.candidate_id == Score.candidate_id)
            .options(
                selectinload(Candidate.score),
                selectinload(Candidate.explanation),
                selectinload(Candidate.decisions),
            )
            .order_by(
                case((Score.total_fit_0_100.is_(None), 1), else_=0),
                Score.total_fit_0_100.desc(),
                Candidate.submitted_at.desc(),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_candidate(self, job_id: str, display_name: str | None = None) -> Candidate:
        """Create a new candidate."""
        candidate = Candidate(
            candidate_id=str(uuid.uuid4()),
            job_id=job_id,
            display_name=display_name,
            status=CandidateStatus.NEW,
        )
        return await self.create(candidate)

    async def update_status(
        self, candidate: Candidate, status: CandidateStatus, error_message: str | None = None
    ) -> Candidate:
        """Update candidate status."""
        update_data = {"status": status}
        if error_message is not None:
            update_data["error_message"] = error_message
        return await self.update(candidate, update_data)
