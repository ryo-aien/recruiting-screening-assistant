from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.models.job import JobStatus
from app.models.candidate import Candidate, CandidateStatus
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.job_repository import JobRepository
from app.schemas.candidate import (
    CandidateCreate,
    CandidateDetail,
    CandidateListItem,
    DecisionDetail,
    DocumentDetail,
    ExplanationDetail,
    ExtractionDetail,
    ScoreDetail,
)


class CandidateService:
    """Service for candidate operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.candidate_repo = CandidateRepository(db)
        self.job_repo = JobRepository(db)

    async def create_candidate(self, job_id: str, data: CandidateCreate) -> CandidateDetail:
        """Create a new candidate for a job."""
        # Verify job exists
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundException(f"Job {job_id} not found")

        # Check if job is closed
        if job.status == JobStatus.CLOSED:
            raise BadRequestException("この求人は応募を締め切っています")

        candidate = await self.candidate_repo.create_candidate(
            job_id=job_id,
            display_name=data.display_name,
        )
        return self._to_detail(candidate)

    async def get_candidate(self, candidate_id: str) -> CandidateDetail:
        """Get a candidate with all details."""
        candidate = await self.candidate_repo.get_by_id_with_details(candidate_id)
        if not candidate:
            raise NotFoundException(f"Candidate {candidate_id} not found")
        return self._to_detail(candidate)

    async def list_candidates(
        self,
        job_id: str,
        limit: int = 100,
        offset: int = 0,
        sort_by_score: bool = True,
    ) -> list[CandidateListItem]:
        """List candidates for a job."""
        # Verify job exists
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundException(f"Job {job_id} not found")

        if sort_by_score:
            candidates = await self.candidate_repo.get_by_job_id_ranked(job_id, limit, offset)
        else:
            candidates = await self.candidate_repo.get_by_job_id(job_id, limit, offset)

        return [self._to_list_item(c) for c in candidates]

    async def update_status(
        self,
        candidate_id: str,
        status: CandidateStatus,
        error_message: str | None = None,
    ) -> CandidateDetail:
        """Update candidate status."""
        candidate = await self.candidate_repo.get_by_id(candidate_id)
        if not candidate:
            raise NotFoundException(f"Candidate {candidate_id} not found")

        candidate = await self.candidate_repo.update_status(candidate, status, error_message)
        return self._to_detail(candidate)

    def _to_list_item(self, candidate: Candidate) -> CandidateListItem:
        """Convert candidate to list item schema."""
        # Get score info
        total_fit = None
        must_gaps_count = 0
        if candidate.score:
            total_fit = candidate.score.total_fit_0_100
            must_gaps_count = len(candidate.score.must_gaps_json or [])

        # Get explanation info
        strengths = []
        concerns = []
        if candidate.explanation and candidate.explanation.explanation_json:
            exp = candidate.explanation.explanation_json
            strengths = exp.get("strengths", [])[:3]
            concerns = exp.get("concerns", [])[:3]

        # Get latest decision
        decided_state = None
        if candidate.decisions:
            latest_decision = max(candidate.decisions, key=lambda d: d.decided_at)
            decided_state = latest_decision.decision

        return CandidateListItem(
            candidate_id=candidate.candidate_id,
            display_name=candidate.display_name,
            status=candidate.status,
            total_fit_0_100=total_fit,
            must_gaps_count=must_gaps_count,
            strengths_top3=strengths,
            concerns_top3=concerns,
            decided_state=decided_state,
            submitted_at=candidate.submitted_at,
        )

    def _to_detail(self, candidate: Candidate) -> CandidateDetail:
        """Convert candidate to detail schema."""
        # Documents
        documents = []
        if hasattr(candidate, "documents") and candidate.documents:
            documents = [
                DocumentDetail(
                    document_id=d.document_id,
                    type=d.type,
                    original_filename=d.original_filename,
                    created_at=d.created_at,
                )
                for d in candidate.documents
            ]

        # Score
        score = None
        if hasattr(candidate, "score") and candidate.score:
            s = candidate.score
            score = ScoreDetail(
                must_score=s.must_score,
                nice_score=s.nice_score,
                year_score=s.year_score,
                role_score=s.role_score,
                total_fit_0_100=s.total_fit_0_100,
                must_gaps=s.must_gaps_json or [],
            )

        # Extraction
        extraction = None
        if hasattr(candidate, "extraction") and candidate.extraction:
            e = candidate.extraction
            extraction = ExtractionDetail(
                job_requirements=e.job_requirements_json,
                candidate_profile=e.candidate_profile_json,
                evidence=e.evidence_json,
            )

        # Explanation
        explanation = None
        if hasattr(candidate, "explanation") and candidate.explanation:
            exp = candidate.explanation.explanation_json or {}
            explanation = ExplanationDetail(
                summary=exp.get("summary"),
                strengths=exp.get("strengths", []),
                concerns=exp.get("concerns", []),
                unknowns=exp.get("unknowns", []),
                must_gaps=exp.get("must_gaps", []),
            )

        # Decisions
        decisions = []
        if hasattr(candidate, "decisions") and candidate.decisions:
            decisions = [
                DecisionDetail(
                    decision_id=d.decision_id,
                    decision=d.decision,
                    reason=d.reason,
                    decided_by=d.decided_by,
                    decided_at=d.decided_at,
                )
                for d in candidate.decisions
            ]

        return CandidateDetail(
            candidate_id=candidate.candidate_id,
            job_id=candidate.job_id,
            display_name=candidate.display_name,
            status=candidate.status,
            error_message=candidate.error_message,
            submitted_at=candidate.submitted_at,
            documents=documents,
            score=score,
            extraction=extraction,
            explanation=explanation,
            decisions=decisions,
        )
