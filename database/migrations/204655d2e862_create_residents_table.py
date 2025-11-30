"""Create residents Table

Revision ID: 204655d2e862
Revises: eaadab72167c
Create Date: 2025-11-30 14:08:41.972142

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = '204655d2e862'
down_revision: Union[str, Sequence[str], None] = 'eaadab72167c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "residents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("family_id", sa.Integer(), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("house_id", sa.Integer(), sa.ForeignKey("houses.id"), nullable=False),
        sa.Column("nik", sa.String(50), nullable=True),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("gender", sa.String(50), nullable=True),
        sa.Column("birth_place", sa.String(100), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

def downgrade() -> None:
    op.drop_table("residents")