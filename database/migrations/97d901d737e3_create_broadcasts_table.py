"""Create broadcasts Table

Revision ID: 97d901d737e3
Revises: a38c2f4ea5e9
Create Date: 2025-11-30 14:26:13.530940

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = '97d901d737e3'
down_revision: Union[str, Sequence[str], None] = 'a38c2f4ea5e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "broadcasts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(100), nullable=True),
        sa.Column("message", sa.Text(255), nullable=True),
        sa.Column("sent_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
    )

def downgrade() -> None:
    op.drop_table("broadcasts")