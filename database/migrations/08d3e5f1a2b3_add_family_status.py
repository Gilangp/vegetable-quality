"""Add status column to families

Revision ID: 08d3e5f1a2b3
Revises: f7a1b2c3d4e5
Create Date: 2025-12-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = '08d3e5f1a2b3'
down_revision: Union[str, Sequence[str], None] = 'f7a1b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add `status` column to families with default 'vacant'
    op.add_column(
        'families',
        sa.Column('status', sa.String(length=20), nullable=False, server_default=sa.text("'vacant'")),
    )


def downgrade() -> None:
    op.drop_column('families', 'status')
