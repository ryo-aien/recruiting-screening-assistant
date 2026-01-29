from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.candidate import Candidate


class Extraction(Base):
    """LLM extraction result model."""

    __tablename__ = "extractions"

    candidate_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("candidates.candidate_id", ondelete="CASCADE"),
        primary_key=True,
    )
    job_requirements_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    candidate_profile_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    evidence_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extract_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="extraction")
