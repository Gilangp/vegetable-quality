"""Create spendings Table

Revision ID: 68722e94b490
Revises: b410e6c28e93
Create Date: 2025-11-30 14:30:40.882000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68722e94b490'
down_revision: Union[str, Sequence[str], None] = 'b410e6c28e93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "spendings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(100), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(255), nullable=True),
        sa.Column("proof_image", sa.String(100), nullable=True),
        sa.Column("proof_file", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("spendings")
