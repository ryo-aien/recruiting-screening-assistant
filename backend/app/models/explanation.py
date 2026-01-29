from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.candidate import Candidate


class Explanation(Base):
    """Generated explanation model."""

    __tablename__ = "explanations"

    candidate_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("candidates.candidate_id", ondelete="CASCADE"),
        primary_key=True,
    )
    explanation_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="explanation")
