"""create project experiences

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-15
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "project_experiences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("member_id", sa.Uuid(), nullable=False),
        sa.Column("project_name", sa.String(length=255), nullable=False),
        sa.Column("customer_name", sa.String(length=255), nullable=True),
        sa.Column("industry", sa.String(length=255), nullable=True),
        sa.Column("period_from", sa.Date(), nullable=True),
        sa.Column("period_to", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=100), nullable=False),
        sa.Column("overview", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["member_id"], ["members.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_experiences_member_id", "project_experiences", ["member_id"])
    op.create_index("ix_project_experiences_deleted_at", "project_experiences", ["deleted_at"])
    op.create_index(
        "ix_project_experiences_member_period_deleted",
        "project_experiences",
        ["member_id", "period_from", "deleted_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_project_experiences_member_period_deleted", table_name="project_experiences")
    op.drop_index("ix_project_experiences_deleted_at", table_name="project_experiences")
    op.drop_index("ix_project_experiences_member_id", table_name="project_experiences")
    op.drop_table("project_experiences")
