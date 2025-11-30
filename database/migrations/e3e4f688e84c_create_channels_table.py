"""Create channels Table

Revision ID: e3e4f688e84c
Revises: 68722e94b490
Create Date: 2025-11-30 14:31:50.680250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3e4f688e84c'
down_revision: Union[str, Sequence[str], None] = '68722e94b490'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "channels",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("account_number", sa.String(100), nullable=True),
        sa.Column("holder_name", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("channels")
