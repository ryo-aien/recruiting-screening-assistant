"""Schemas for LLM extraction results."""

from typing import Any

from pydantic import BaseModel, Field


class MustRequirement(BaseModel):
    """Must requirement schema."""

    id: str
    text: str
    skill_tags: list[str] = Field(default_factory=list)


class NiceRequirement(BaseModel):
    """Nice-to-have requirement schema."""

    id: str
    text: str
    skill_tags: list[str] = Field(default_factory=list)


class JobRequirements(BaseModel):
    """Job requirements extracted from job posting."""

    must: list[MustRequirement] = Field(default_factory=list)
    nice: list[NiceRequirement] = Field(default_factory=list)
    role_expectation: str | None = None
    year_requirements: dict[str, float | None] = Field(default_factory=dict)


class CandidateProfile(BaseModel):
    """Candidate profile extracted from resume."""

    skills: list[str] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=list)
    experience_years: dict[str, float | None] = Field(default_factory=dict)
    highlights: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)


class Evidence(BaseModel):
    """Evidence quotes supporting extraction."""

    job: dict[str, str] = Field(default_factory=dict)
    candidate: dict[str, str] = Field(default_factory=dict)


class ExtractionResult(BaseModel):
    """Complete extraction result from LLM."""

    job_requirements: JobRequirements
    candidate_profile: CandidateProfile
    evidence: Evidence

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExtractionResult":
        """Create from raw dictionary (LLM output)."""
        return cls(
            job_requirements=JobRequirements(**data.get("job_requirements", {})),
            candidate_profile=CandidateProfile(**data.get("candidate_profile", {})),
            evidence=Evidence(**data.get("evidence", {})),
        )
