"""Create verivication_results Table

Revision ID: a2904c974190
Revises: e3e4f688e84c
Create Date: 2025-11-30 14:32:29.300224

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = 'a2904c974190'
down_revision: Union[str, Sequence[str], None] = 'e3e4f688e84c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "verification_results",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("resident_id", sa.Integer(), sa.ForeignKey("residents.id"), nullable=False),
        sa.Column("vegetable_name", sa.String(100), nullable=True),
        sa.Column("image", sa.String(100), nullable=True),
        sa.Column("result", sa.String(255), nullable=True),
        sa.Column("is_valid_for_marketplace", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
    )

def downgrade() -> None:
    op.drop_table("verification_results")