from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.candidate import Candidate


class JobType(str, Enum):
    TEXT_EXTRACT = "TEXT_EXTRACT"
    LLM_EXTRACT = "LLM_EXTRACT"
    EMBED = "EMBED"
    SCORE = "SCORE"
    EXPLAIN = "EXPLAIN"


class QueueStatus(str, Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


class JobsQueue(Base):
    """Async job queue model using DB polling."""

    __tablename__ = "jobs_queue"

    queue_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False
    )
    job_type: Mapped[JobType] = mapped_column(String(20), nullable=False)
    status: Mapped[QueueStatus] = mapped_column(
        String(20), default=QueueStatus.READY, nullable=False
    )
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="queue_jobs")
