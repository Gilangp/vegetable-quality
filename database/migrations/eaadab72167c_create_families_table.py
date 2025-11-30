"""Create families Table

Revision ID: eaadab72167c
Revises: 6a1b7295d422
Create Date: 2025-11-30 14:07:29.813569

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eaadab72167c'
down_revision: Union[str, Sequence[str], None] = '6a1b7295d422'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "families",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("family_number", sa.String(50), nullable=True),
        sa.Column("head_resident_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("families")
