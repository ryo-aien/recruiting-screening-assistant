from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.candidate import CandidateStatus


class CandidateCreate(BaseModel):
    """Schema for creating a new candidate."""

    display_name: str | None = Field(None, max_length=255)


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate."""

    display_name: str | None = Field(None, max_length=255)
    status: CandidateStatus | None = None


class CandidateListItem(BaseModel):
    """Schema for candidate list item (for ranking display)."""

    candidate_id: str
    display_name: str | None
    status: CandidateStatus
    total_fit_0_100: int | None = None
    must_gaps_count: int = 0
    strengths_top3: list[str] = []
    concerns_top3: list[str] = []
    decided_state: str | None = None
    submitted_at: datetime

    model_config = {"from_attributes": True}


class ScoreDetail(BaseModel):
    """Score breakdown detail."""

    must_score: float
    nice_score: float
    year_score: float
    role_score: float
    total_fit_0_100: int
    must_gaps: list[str] = []


class ExtractionDetail(BaseModel):
    """Extraction result detail."""

    job_requirements: dict[str, Any] | None = None
    candidate_profile: dict[str, Any] | None = None
    evidence: dict[str, Any] | None = None


class ExplanationDetail(BaseModel):
    """Explanation detail."""

    summary: str | None = None
    strengths: list[str] = []
    concerns: list[str] = []
    unknowns: list[str] = []
    must_gaps: list[str] = []


class DocumentDetail(BaseModel):
    """Document detail."""

    document_id: str
    type: str
    original_filename: str
    created_at: datetime


class DecisionDetail(BaseModel):
    """Decision detail."""

    decision_id: str
    decision: str
    reason: str | None
    decided_by: str | None
    decided_at: datetime


class CandidateDetail(BaseModel):
    """Schema for candidate detail with all related data."""

    candidate_id: str
    job_id: str
    display_name: str | None
    status: CandidateStatus
    error_message: str | None
    submitted_at: datetime
    documents: list[DocumentDetail] = []
    score: ScoreDetail | None = None
    extraction: ExtractionDetail | None = None
    explanation: ExplanationDetail | None = None
    decisions: list[DecisionDetail] = []

    model_config = {"from_attributes": True}
