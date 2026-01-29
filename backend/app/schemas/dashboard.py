from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class RecentCandidate(BaseModel):
    candidate_id: str
    display_name: str | None
    job_id: str
    job_title: str
    status: Literal["NEW", "PROCESSING", "DONE", "ERROR"]
    total_fit_0_100: int | None
    submitted_at: datetime


class DashboardStatsResponse(BaseModel):
    total_jobs: int
    total_candidates: int
    candidates_by_status: dict[str, int]
    candidates_by_decision: dict[str, int]
    recent_candidates: list[RecentCandidate]
