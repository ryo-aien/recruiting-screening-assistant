from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.candidate import Candidate
from app.models.decision import Decision
from app.models.job import Job
from app.models.score import Score
from app.schemas.dashboard import DashboardStatsResponse, RecentCandidate

router = APIRouter()


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics."""
    # Total jobs
    total_jobs_result = await db.execute(select(func.count(Job.job_id)))
    total_jobs = total_jobs_result.scalar() or 0

    # Total candidates
    total_candidates_result = await db.execute(select(func.count(Candidate.candidate_id)))
    total_candidates = total_candidates_result.scalar() or 0

    # Candidates by status
    status_counts = {}
    for status in ["NEW", "PROCESSING", "DONE", "ERROR"]:
        result = await db.execute(
            select(func.count(Candidate.candidate_id)).where(Candidate.status == status)
        )
        status_counts[status] = result.scalar() or 0

    # Candidates by decision
    # Get latest decision for each candidate
    subquery = (
        select(
            Decision.candidate_id,
            Decision.decision,
            func.row_number()
            .over(partition_by=Decision.candidate_id, order_by=Decision.decided_at.desc())
            .label("rn"),
        )
    ).subquery()

    latest_decisions = select(subquery.c.candidate_id, subquery.c.decision).where(
        subquery.c.rn == 1
    )

    decision_counts = {"pass": 0, "hold": 0, "reject": 0, "undecided": 0}

    # Count by decision type
    for decision_type in ["pass", "hold", "reject"]:
        result = await db.execute(
            select(func.count()).select_from(
                latest_decisions.where(subquery.c.decision == decision_type).subquery()
            )
        )
        decision_counts[decision_type] = result.scalar() or 0

    # Count undecided (candidates without any decision)
    candidates_with_decision = select(Decision.candidate_id).distinct()
    undecided_result = await db.execute(
        select(func.count(Candidate.candidate_id)).where(
            Candidate.candidate_id.notin_(candidates_with_decision)
        )
    )
    decision_counts["undecided"] = undecided_result.scalar() or 0

    # Recent candidates (last 10)
    recent_candidates_query = (
        select(
            Candidate.candidate_id,
            Candidate.display_name,
            Candidate.job_id,
            Candidate.status,
            Candidate.submitted_at,
            Job.title.label("job_title"),
            Score.total_fit_0_100,
        )
        .outerjoin(Job, Candidate.job_id == Job.job_id)
        .outerjoin(Score, Candidate.candidate_id == Score.candidate_id)
        .order_by(Candidate.submitted_at.desc())
        .limit(10)
    )

    recent_result = await db.execute(recent_candidates_query)
    recent_rows = recent_result.all()

    recent_candidates = [
        RecentCandidate(
            candidate_id=row.candidate_id,
            display_name=row.display_name,
            job_id=row.job_id,
            job_title=row.job_title or "不明",
            status=row.status,
            total_fit_0_100=row.total_fit_0_100,
            submitted_at=row.submitted_at,
        )
        for row in recent_rows
    ]

    return DashboardStatsResponse(
        total_jobs=total_jobs,
        total_candidates=total_candidates,
        candidates_by_status=status_counts,
        candidates_by_decision=decision_counts,
        recent_candidates=recent_candidates,
    )
