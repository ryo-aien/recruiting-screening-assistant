"""Add status to jobs table

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add status column to jobs table
    # OPEN: 募集中（応募受付可）
    # CLOSED: 選考完了（応募締め切り）
    op.add_column(
        "jobs",
        sa.Column("status", sa.String(20), server_default="OPEN", nullable=False),
    )
    op.create_index("ix_jobs_status", "jobs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_jobs_status", table_name="jobs")
    op.drop_column("jobs", "status")
