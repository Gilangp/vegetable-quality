"""Create setting Table

Revision ID: af61cd517646
Revises: aad6ebea8181
Create Date: 2025-11-30 14:34:09.662678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af61cd517646'
down_revision: Union[str, Sequence[str], None] = 'aad6ebea8181'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "settings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("key", sa.String(100), nullable=True),
        sa.Column("value", sa.Text(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("settings")
