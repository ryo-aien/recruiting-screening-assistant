from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.candidate import Candidate


class EmbeddingKind(str, Enum):
    CANDIDATE_SUMMARY = "candidate_summary"
    NICE_REQ = "nice_req"


class Embedding(Base):
    """Embedding vector model for semantic similarity."""

    __tablename__ = "embeddings"

    embedding_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[EmbeddingKind] = mapped_column(String(50), nullable=False)
    ref_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vector: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="embeddings")
