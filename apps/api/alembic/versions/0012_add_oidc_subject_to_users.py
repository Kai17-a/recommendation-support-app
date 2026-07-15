"""add oidc subject to users

Revision ID: 0012
Revises: 0011
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0012"
down_revision: str | None = "0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("oidc_subject", sa.String(length=255), nullable=True))
    op.create_unique_constraint("uq_users_oidc_subject", "users", ["oidc_subject"])


def downgrade() -> None:
    op.drop_constraint("uq_users_oidc_subject", "users", type_="unique")
    op.drop_column("users", "oidc_subject")
