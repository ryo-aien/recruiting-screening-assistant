from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class WeightsSchema(BaseModel):
    """Schema for score weights."""

    must: float = Field(0.45, ge=0, le=1)
    nice: float = Field(0.20, ge=0, le=1)
    year: float = Field(0.20, ge=0, le=1)
    role: float = Field(0.15, ge=0, le=1)


class ScoreConfigCreate(BaseModel):
    """Schema for creating/updating score config."""

    weights: WeightsSchema = Field(default_factory=WeightsSchema)
    must_cap_enabled: bool = True
    must_cap_value: float = Field(20.0, ge=0, le=100)
    nice_top_n: int = Field(3, ge=1, le=10)
    role_distance: dict[str, dict[str, float]] | None = None


class ScoreConfigResponse(BaseModel):
    """Schema for score config response."""

    version: int
    weights_json: dict[str, float]
    must_cap_enabled: bool
    must_cap_value: float
    nice_top_n: int
    role_distance_json: dict[str, dict[str, float]]
    created_at: datetime

    model_config = {"from_attributes": True}
