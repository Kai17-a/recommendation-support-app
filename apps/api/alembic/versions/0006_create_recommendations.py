"""create recommendations
Revision ID: 0006
Revises: 0005
Create Date: 2026-07-15
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "recommendations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("member_id", sa.Uuid(), nullable=False),
        sa.Column("purpose", sa.String(255), nullable=False),
        sa.Column("target_name", sa.String(255)),
        sa.Column("target_requirements", sa.Text()),
        sa.Column("emphasis_points", sa.Text()),
        sa.Column("tone", sa.String(100)),
        sa.Column("output_format", sa.String(100)),
        sa.Column("status", sa.String(100), nullable=False),
        sa.Column("finalized_at", sa.DateTime(timezone=True)),
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
    )
    op.create_table(
        "recommendation_versions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("recommendation_id", sa.Uuid(), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("version_type", sa.String(100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_by", sa.Uuid()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["recommendation_id"], ["recommendations.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.UniqueConstraint("recommendation_id", "version_no"),
    )
    op.create_index(
        "ix_recommendations_member_status_deleted",
        "recommendations",
        ["member_id", "status", "deleted_at"],
    )


def downgrade() -> None:
    op.drop_table("recommendation_versions")
    op.drop_table("recommendations")
