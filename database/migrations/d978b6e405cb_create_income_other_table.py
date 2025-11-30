"""Create income_other Table

Revision ID: d978b6e405cb
Revises: 6479952f175e
Create Date: 2025-11-30 14:29:29.901834

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd978b6e405cb'
down_revision: Union[str, Sequence[str], None] = '6479952f175e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "income_other",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("description", sa.Text(255), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("income_other")
