from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.candidate import Candidate


class DocumentType(str, Enum):
    RESUME = "resume"
    CV = "cv"


class Document(Base):
    """Uploaded document model."""

    __tablename__ = "documents"

    document_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[DocumentType] = mapped_column(String(20), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    object_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    text_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="documents")
