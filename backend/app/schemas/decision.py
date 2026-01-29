from datetime import datetime

from pydantic import BaseModel, Field

from app.models.decision import DecisionType


class DecisionCreate(BaseModel):
    """Schema for creating a decision."""

    decision: DecisionType = Field(..., description="Decision: pass, hold, or reject")
    reason: str | None = Field(None, max_length=2000)
    decided_by: str | None = Field(None, max_length=255)


class DecisionResponse(BaseModel):
    """Schema for decision response."""

    decision_id: str
    candidate_id: str
    decision: DecisionType
    reason: str | None
    decided_by: str | None
    decided_at: datetime

    model_config = {"from_attributes": True}
