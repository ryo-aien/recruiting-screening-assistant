from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.decision import Decision
    from app.models.document import Document
    from app.models.embedding import Embedding
    from app.models.explanation import Explanation
    from app.models.extraction import Extraction
    from app.models.job import Job
    from app.models.jobs_queue import JobsQueue
    from app.models.score import Score


class CandidateStatus(str, Enum):
    NEW = "NEW"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    ERROR = "ERROR"


class Candidate(Base):
    """Candidate/applicant model."""

    __tablename__ = "candidates"

    candidate_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False
    )
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[CandidateStatus] = mapped_column(
        String(20), default=CandidateStatus.NEW, nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="candidates")
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="candidate", cascade="all, delete-orphan"
    )
    extraction: Mapped["Extraction | None"] = relationship(
        "Extraction", back_populates="candidate", uselist=False, cascade="all, delete-orphan"
    )
    embeddings: Mapped[list["Embedding"]] = relationship(
        "Embedding", back_populates="candidate", cascade="all, delete-orphan"
    )
    score: Mapped["Score | None"] = relationship(
        "Score", back_populates="candidate", uselist=False, cascade="all, delete-orphan"
    )
    explanation: Mapped["Explanation | None"] = relationship(
        "Explanation", back_populates="candidate", uselist=False, cascade="all, delete-orphan"
    )
    decisions: Mapped[list["Decision"]] = relationship(
        "Decision", back_populates="candidate", cascade="all, delete-orphan"
    )
    queue_jobs: Mapped[list["JobsQueue"]] = relationship(
        "JobsQueue", back_populates="candidate", cascade="all, delete-orphan"
    )
