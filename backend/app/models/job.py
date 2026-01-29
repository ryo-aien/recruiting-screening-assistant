from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.candidate import Candidate


class JobStatus(str, Enum):
    OPEN = "OPEN"      # 募集中（応募受付可）
    CLOSED = "CLOSED"  # 選考完了（応募締め切り）


class Job(Base):
    """Job posting model."""

    __tablename__ = "jobs"

    job_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    job_text_raw: Mapped[str] = mapped_column(Text, nullable=False)
    requirements_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[JobStatus] = mapped_column(
        String(20), default=JobStatus.OPEN, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    candidates: Mapped[list["Candidate"]] = relationship(
        "Candidate", back_populates="job", cascade="all, delete-orphan"
    )
