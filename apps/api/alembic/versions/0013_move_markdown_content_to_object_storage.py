"""move markdown content to object storage

Revision ID: 0013
Revises: 0012
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0013"
down_revision: str | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1 FROM markdown_imports
            WHERE raw_content IS NOT NULL AND file_storage_key IS NULL
          ) THEN
            RAISE EXCEPTION
              'raw_content must be copied to object storage before migration 0013';
          END IF;
        END $$;
        """
    )
    op.drop_column("markdown_imports", "raw_content")


def downgrade() -> None:
    op.add_column("markdown_imports", sa.Column("raw_content", sa.Text(), nullable=True))
