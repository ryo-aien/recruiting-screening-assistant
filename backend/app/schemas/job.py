from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.job import JobStatus


class JobCreate(BaseModel):
    """Schema for creating a new job."""

    title: str = Field(..., min_length=1, max_length=255)
    job_text_raw: str = Field(..., min_length=1)
    requirements_json: dict[str, Any] | None = None


class JobUpdate(BaseModel):
    """Schema for updating a job."""

    title: str | None = Field(None, min_length=1, max_length=255)
    job_text_raw: str | None = Field(None, min_length=1)
    requirements_json: dict[str, Any] | None = None
    status: JobStatus | None = None


class JobListItem(BaseModel):
    """Schema for job list item."""

    job_id: str
    title: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    candidate_count: int = 0

    model_config = {"from_attributes": True}


class JobDetail(BaseModel):
    """Schema for job detail."""

    job_id: str
    title: str
    job_text_raw: str
    requirements_json: dict[str, Any] | None
    status: JobStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
