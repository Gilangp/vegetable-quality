"""Create incomes Table

Revision ID: b410e6c28e93
Revises: d978b6e405cb
Create Date: 2025-11-30 14:30:08.265504

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b410e6c28e93'
down_revision: Union[str, Sequence[str], None] = 'd978b6e405cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "incomes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("related_table", sa.String(100), nullable=True),
        sa.Column("related_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("incomes")
