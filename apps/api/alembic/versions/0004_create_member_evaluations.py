"""create member evaluations

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-15
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "member_evaluations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("member_id", sa.Uuid(), nullable=False),
        sa.Column("project_experience_id", sa.Uuid()),
        sa.Column("evaluation_type", sa.String(100), nullable=False),
        sa.Column("period_from", sa.Date()),
        sa.Column("period_to", sa.Date()),
        sa.Column("evaluation_date", sa.Date(), nullable=False),
        sa.Column("strengths", sa.Text()),
        sa.Column("areas_for_improvement", sa.Text()),
        sa.Column("leadership", sa.Text()),
        sa.Column("communication", sa.Text()),
        sa.Column("problem_solving", sa.Text()),
        sa.Column("initiative", sa.Text()),
        sa.Column("manager_comment", sa.Text()),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"]),
        sa.ForeignKeyConstraint(["project_experience_id"], ["project_experiences.id"]),
    )
    op.create_index(
        "ix_member_evaluations_member_date_deleted",
        "member_evaluations",
        ["member_id", "evaluation_date", "deleted_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_member_evaluations_member_date_deleted", table_name="member_evaluations")
    op.drop_table("member_evaluations")
