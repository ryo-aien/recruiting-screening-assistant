"""SQLAlchemy models for the worker (mirrors backend models)."""

from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from worker.database import Base


class CandidateStatus(str, Enum):
    NEW = "NEW"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    ERROR = "ERROR"


class DocumentType(str, Enum):
    RESUME = "resume"
    CV = "cv"


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


class EmbeddingKind(str, Enum):
    CANDIDATE_SUMMARY = "candidate_summary"
    NICE_REQ = "nice_req"


class Job(Base):
    """Job posting model."""

    __tablename__ = "jobs"

    job_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    job_text_raw: Mapped[str] = mapped_column(Text, nullable=False)
    requirements_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Candidate(Base):
    """Candidate model."""

    __tablename__ = "candidates"

    candidate_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.job_id"), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="NEW")
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Document(Base):
    """Document model."""

    __tablename__ = "documents"

    document_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidates.candidate_id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    object_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    text_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Extraction(Base):
    """Extraction model."""

    __tablename__ = "extractions"

    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidates.candidate_id"), primary_key=True
    )
    job_requirements_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    candidate_profile_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    evidence_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extract_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Embedding(Base):
    """Embedding model."""

    __tablename__ = "embeddings"

    embedding_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidates.candidate_id"), nullable=False
    )
    kind: Mapped[str] = mapped_column(String(50), nullable=False)
    ref_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vector: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Score(Base):
    """Score model."""

    __tablename__ = "scores"

    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidates.candidate_id"), primary_key=True
    )
    must_score: Mapped[float] = mapped_column(Float, default=0.0)
    nice_score: Mapped[float] = mapped_column(Float, default=0.0)
    year_score: Mapped[float] = mapped_column(Float, default=0.0)
    role_score: Mapped[float] = mapped_column(Float, default=0.0)
    total_fit_0_100: Mapped[int] = mapped_column(Integer, default=0)
    must_gaps_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    score_config_version: Mapped[int] = mapped_column(Integer, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Explanation(Base):
    """Explanation model."""

    __tablename__ = "explanations"

    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidates.candidate_id"), primary_key=True
    )
    explanation_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ScoreConfig(Base):
    """Score config model."""

    __tablename__ = "score_config"

    version: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    weights_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    must_cap_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    must_cap_value: Mapped[float] = mapped_column(Float, default=20.0)
    nice_top_n: Mapped[int] = mapped_column(Integer, default=3)
    role_distance_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class JobsQueue(Base):
    """Job queue model."""

    __tablename__ = "jobs_queue"

    queue_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    candidate_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidates.candidate_id"), nullable=False
    )
    job_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="READY")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
