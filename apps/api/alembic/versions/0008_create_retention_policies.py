"""create retention policies

Revision ID: 0008
Revises: 0007
Create Date: 2026-07-15
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "retention_policies",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("target_type", sa.String(100), nullable=False, unique=True),
        sa.Column("retention_months", sa.Integer(), nullable=False),
        sa.Column("purge_enabled", sa.Boolean(), nullable=False),
        sa.Column("require_manual_approval", sa.Boolean(), nullable=False),
        sa.Column("created_by", sa.Uuid()),
        sa.Column("updated_by", sa.Uuid()),
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
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
    )


def downgrade() -> None:
    op.drop_table("retention_policies")
