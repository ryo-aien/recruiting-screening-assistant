"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Jobs table
    op.create_table(
        "jobs",
        sa.Column("job_id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("job_text_raw", sa.Text, nullable=False),
        sa.Column("requirements_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # Score config table
    op.create_table(
        "score_config",
        sa.Column("version", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("weights_json", sa.JSON, nullable=False),
        sa.Column("must_cap_enabled", sa.Boolean, default=True, nullable=False),
        sa.Column("must_cap_value", sa.Float, default=20.0, nullable=False),
        sa.Column("nice_top_n", sa.Integer, default=3, nullable=False),
        sa.Column("role_distance_json", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )

    # Candidates table
    op.create_table(
        "candidates",
        sa.Column("candidate_id", sa.String(36), primary_key=True),
        sa.Column(
            "job_id",
            sa.String(36),
            sa.ForeignKey("jobs.job_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("status", sa.String(20), default="NEW", nullable=False),
        sa.Column("error_message", sa.String(1000), nullable=True),
        sa.Column("submitted_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_candidates_job_id", "candidates", ["job_id"])
    op.create_index("ix_candidates_status", "candidates", ["status"])

    # Documents table
    op.create_table(
        "documents",
        sa.Column("document_id", sa.String(36), primary_key=True),
        sa.Column(
            "candidate_id",
            sa.String(36),
            sa.ForeignKey("candidates.candidate_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("object_uri", sa.String(500), nullable=False),
        sa.Column("text_uri", sa.String(500), nullable=True),
        sa.Column("file_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_documents_candidate_id", "documents", ["candidate_id"])

    # Extractions table
    op.create_table(
        "extractions",
        sa.Column(
            "candidate_id",
            sa.String(36),
            sa.ForeignKey("candidates.candidate_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("job_requirements_json", sa.JSON, nullable=True),
        sa.Column("candidate_profile_json", sa.JSON, nullable=True),
        sa.Column("evidence_json", sa.JSON, nullable=True),
        sa.Column("llm_model", sa.String(100), nullable=True),
        sa.Column("extract_version", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )

    # Embeddings table
    op.create_table(
        "embeddings",
        sa.Column("embedding_id", sa.String(36), primary_key=True),
        sa.Column(
            "candidate_id",
            sa.String(36),
            sa.ForeignKey("candidates.candidate_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(50), nullable=False),
        sa.Column("ref_id", sa.String(100), nullable=True),
        sa.Column("vector", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_embeddings_candidate_id", "embeddings", ["candidate_id"])

    # Scores table
    op.create_table(
        "scores",
        sa.Column(
            "candidate_id",
            sa.String(36),
            sa.ForeignKey("candidates.candidate_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("must_score", sa.Float, default=0.0, nullable=False),
        sa.Column("nice_score", sa.Float, default=0.0, nullable=False),
        sa.Column("year_score", sa.Float, default=0.0, nullable=False),
        sa.Column("role_score", sa.Float, default=0.0, nullable=False),
        sa.Column("total_fit_0_100", sa.Integer, default=0, nullable=False),
        sa.Column("must_gaps_json", sa.JSON, nullable=True),
        sa.Column("score_config_version", sa.Integer, nullable=False),
        sa.Column("computed_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )

    # Explanations table
    op.create_table(
        "explanations",
        sa.Column(
            "candidate_id",
            sa.String(36),
            sa.ForeignKey("candidates.candidate_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("explanation_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )

    # Decisions table
    op.create_table(
        "decisions",
        sa.Column("decision_id", sa.String(36), primary_key=True),
        sa.Column(
            "candidate_id",
            sa.String(36),
            sa.ForeignKey("candidates.candidate_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("decision", sa.String(20), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("decided_by", sa.String(255), nullable=True),
        sa.Column("decided_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_decisions_candidate_id", "decisions", ["candidate_id"])

    # Audit events table
    op.create_table(
        "audit_events",
        sa.Column("event_id", sa.String(36), primary_key=True),
        sa.Column("actor_id", sa.String(255), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=True),
        sa.Column("payload_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_events_entity_type", "audit_events", ["entity_type"])
    op.create_index("ix_audit_events_created_at", "audit_events", ["created_at"])

    # Jobs queue table
    op.create_table(
        "jobs_queue",
        sa.Column("queue_id", sa.String(36), primary_key=True),
        sa.Column(
            "candidate_id",
            sa.String(36),
            sa.ForeignKey("candidates.candidate_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("job_type", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), default="READY", nullable=False),
        sa.Column("attempts", sa.Integer, default=0, nullable=False),
        sa.Column("last_error", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_jobs_queue_status", "jobs_queue", ["status"])
    op.create_index("ix_jobs_queue_job_type", "jobs_queue", ["job_type"])
    op.create_index("ix_jobs_queue_candidate_id", "jobs_queue", ["candidate_id"])

    # Insert default score config
    op.execute(
        """
        INSERT INTO score_config (weights_json, must_cap_enabled, must_cap_value, nice_top_n, role_distance_json)
        VALUES (
            '{"must": 0.45, "nice": 0.20, "year": 0.20, "role": 0.15}',
            TRUE,
            20.0,
            3,
            '{"IC": {"IC": 1.0, "Lead": 0.7, "Manager": 0.3}, "Lead": {"IC": 0.7, "Lead": 1.0, "Manager": 0.7}, "Manager": {"IC": 0.3, "Lead": 0.7, "Manager": 1.0}}'
        )
    """
    )


def downgrade() -> None:
    op.drop_table("jobs_queue")
    op.drop_table("audit_events")
    op.drop_table("decisions")
    op.drop_table("explanations")
    op.drop_table("scores")
    op.drop_table("embeddings")
    op.drop_table("extractions")
    op.drop_table("documents")
    op.drop_table("candidates")
    op.drop_table("score_config")
    op.drop_table("jobs")
