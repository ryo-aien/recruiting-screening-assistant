from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.candidate import Candidate


class DecisionType(str, Enum):
    PASS = "pass"
    HOLD = "hold"
    REJECT = "reject"


class Decision(Base):
    """Human decision model."""

    __tablename__ = "decisions"

    decision_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False
    )
    decision: Mapped[DecisionType] = mapped_column(String(20), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="decisions")
