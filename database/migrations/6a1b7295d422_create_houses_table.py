"""Create houses Table

Revision ID: 6a1b7295d422
Revises: ae3529fc7b78
Create Date: 2025-11-30 14:05:59.868363

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = '6a1b7295d422'
down_revision: Union[str, Sequence[str], None] = 'ae3529fc7b78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "houses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("house_number", sa.String(50), nullable=True),
        sa.Column("address", sa.Text(255), nullable=True),
        sa.Column("rt", sa.String(10), nullable=True),
        sa.Column("rw", sa.String(10), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

def downgrade() -> None:
    op.drop_table("houses")