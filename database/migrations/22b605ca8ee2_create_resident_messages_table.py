"""Create resident_messages Table

Revision ID: 22b605ca8ee2
Revises: d2eb3264700f
Create Date: 2025-11-30 14:25:02.773960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22b605ca8ee2'
down_revision: Union[str, Sequence[str], None] = 'd2eb3264700f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "resident_messages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("resident_id", sa.Integer(), sa.ForeignKey("residents.id"), nullable=False),
        sa.Column("subject", sa.String(100), nullable=True),
        sa.Column("message", sa.Text(255), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("resident_messages")
