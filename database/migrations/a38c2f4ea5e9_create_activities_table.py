"""Create activities Table

Revision ID: a38c2f4ea5e9
Revises: 22b605ca8ee2
Create Date: 2025-11-30 14:25:39.591462

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a38c2f4ea5e9'
down_revision: Union[str, Sequence[str], None] = '22b605ca8ee2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "activities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(100), nullable=True),
        sa.Column("description", sa.Text(255), nullable=True),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("location", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("activities")
