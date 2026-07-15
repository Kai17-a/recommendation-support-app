"""create markdown imports

Revision ID: 0010
Revises: 0009
Create Date: 2026-07-15
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "markdown_imports",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("member_id", sa.Uuid(), nullable=False),
        sa.Column("project_experience_id", sa.Uuid(), nullable=False),
        sa.Column("project_report_id", sa.Uuid()),
        sa.Column("original_file_name", sa.String(255), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("raw_content", sa.Text()),
        sa.Column("file_storage_key", sa.String(2048)),
        sa.Column("file_retained", sa.Boolean(), nullable=False),
        sa.Column("template_version", sa.String(100), nullable=False),
        sa.Column("import_status", sa.String(100), nullable=False),
        sa.Column("imported_by", sa.Uuid()),
        sa.Column(
            "imported_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"]),
        sa.ForeignKeyConstraint(["project_experience_id"], ["project_experiences.id"]),
        sa.ForeignKeyConstraint(["project_report_id"], ["project_reports.id"]),
        sa.ForeignKeyConstraint(["imported_by"], ["users.id"]),
    )
    op.create_index(
        "ix_markdown_imports_hash_member_project",
        "markdown_imports",
        ["content_hash", "member_id", "project_experience_id"],
        unique=True,
    )
    op.create_table(
        "markdown_import_warnings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("markdown_import_id", sa.Uuid(), nullable=False),
        sa.Column("warning_code", sa.String(100), nullable=False),
        sa.Column("field_name", sa.String(100)),
        sa.Column("source_text", sa.Text()),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("resolution_status", sa.String(100), nullable=False),
        sa.Column("resolved_by", sa.Uuid()),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["markdown_import_id"], ["markdown_imports.id"]),
        sa.ForeignKeyConstraint(["resolved_by"], ["users.id"]),
    )
    op.create_index(
        "ix_markdown_import_warnings_markdown_import_id",
        "markdown_import_warnings",
        ["markdown_import_id"],
    )


def downgrade() -> None:
    op.drop_table("markdown_import_warnings")
    op.drop_table("markdown_imports")
