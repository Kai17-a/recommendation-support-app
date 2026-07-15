"""create AI jobs, analyses, and settings

Revision ID: 0009
Revises: 0008
Create Date: 2026-07-15
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("job_type", sa.String(100), nullable=False),
        sa.Column("target_type", sa.String(100), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(100), nullable=False),
        sa.Column("requested_by", sa.Uuid()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("error_message", sa.Text()),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"]),
    )
    op.create_index("ix_ai_jobs_status_created_at", "ai_jobs", ["status", "created_at"])
    op.create_index("ix_ai_jobs_target", "ai_jobs", ["target_type", "target_id"])

    op.create_table(
        "ai_analyses",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("ai_job_id", sa.Uuid(), nullable=False, unique=True),
        sa.Column("target_type", sa.String(100), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(100), nullable=False),
        sa.Column("model", sa.String(255), nullable=False),
        sa.Column("prompt_version", sa.String(100), nullable=False),
        sa.Column("analysis_result", sa.JSON(), nullable=False),
        sa.Column("evidence_map", sa.JSON(), nullable=False),
        sa.Column("source_snapshot", sa.Text(), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["ai_job_id"], ["ai_jobs.id"]),
    )
    op.create_index(
        "ix_ai_analyses_target", "ai_analyses", ["target_type", "target_id", "deleted_at"]
    )

    op.create_table(
        "ai_settings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("provider", sa.String(100), nullable=False),
        sa.Column("base_url", sa.String(2048), nullable=False),
        sa.Column("model", sa.String(255), nullable=False),
        sa.Column("api_key_secret_ref", sa.String(255), nullable=False),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False),
        sa.Column("max_retries", sa.Integer(), nullable=False),
        sa.Column("prompt_version", sa.String(100), nullable=False),
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
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
    )


def downgrade() -> None:
    op.drop_table("ai_settings")
    op.drop_table("ai_analyses")
    op.drop_table("ai_jobs")
