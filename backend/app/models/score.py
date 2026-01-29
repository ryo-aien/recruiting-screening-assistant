from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.candidate import Candidate


class Score(Base):
    """Calculated score model."""

    __tablename__ = "scores"

    candidate_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("candidates.candidate_id", ondelete="CASCADE"),
        primary_key=True,
    )
    must_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    nice_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    year_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    role_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_fit_0_100: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    must_gaps_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    score_config_version: Mapped[int] = mapped_column(Integer, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="score")
