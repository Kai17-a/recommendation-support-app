"""create recommendation evidences

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-15
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "recommendation_evidences",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("recommendation_version_id", sa.Uuid(), nullable=False),
        sa.Column("paragraph_no", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(100), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("evidence_text", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["recommendation_version_id"], ["recommendation_versions.id"]),
    )
    op.create_index(
        "ix_recommendation_evidences_version_paragraph_deleted",
        "recommendation_evidences",
        ["recommendation_version_id", "paragraph_no", "deleted_at"],
    )


def downgrade() -> None:
    op.drop_table("recommendation_evidences")
