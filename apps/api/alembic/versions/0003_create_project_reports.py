"""create project reports

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-15
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "project_reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_experience_id", sa.Uuid(), nullable=False),
        sa.Column("report_type", sa.String(length=100), nullable=False),
        sa.Column("period_from", sa.Date(), nullable=True),
        sa.Column("period_to", sa.Date(), nullable=True),
        sa.Column("report_date", sa.Date(), nullable=False),
        sa.Column("work_detail", sa.Text(), nullable=True),
        sa.Column("achievements", sa.Text(), nullable=True),
        sa.Column("technologies", sa.Text(), nullable=True),
        sa.Column("difficulties", sa.Text(), nullable=True),
        sa.Column("improvements", sa.Text(), nullable=True),
        sa.Column("member_comment", sa.Text(), nullable=True),
        sa.Column("manager_comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_experience_id"], ["project_experiences.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_project_reports_project_experience_id", "project_reports", ["project_experience_id"]
    )
    op.create_index("ix_project_reports_report_date", "project_reports", ["report_date"])
    op.create_index("ix_project_reports_deleted_at", "project_reports", ["deleted_at"])


def downgrade() -> None:
    op.drop_index("ix_project_reports_deleted_at", table_name="project_reports")
    op.drop_index("ix_project_reports_report_date", table_name="project_reports")
    op.drop_index("ix_project_reports_project_experience_id", table_name="project_reports")
    op.drop_table("project_reports")
