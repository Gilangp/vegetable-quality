"""Create income_categories Table

Revision ID: 6ec985b81b4d
Revises: 97d901d737e3
Create Date: 2025-11-30 14:27:57.704817

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = '6ec985b81b4d'
down_revision: Union[str, Sequence[str], None] = '97d901d737e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "income_categories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("description", sa.Text(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("income_categories")