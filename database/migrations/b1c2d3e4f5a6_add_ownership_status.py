"""Add ownership_status to families

Revision ID: b1c2d3e4f5a6
Revises: 2b4f6a9c5d7e
Create Date: 2025-12-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, Sequence[str], None] = '2b4f6a9c5d7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add ownership_status column to families
    op.add_column('families', sa.Column('ownership_status', sa.String(length=50), nullable=True))


def downgrade() -> None:
    # Drop ownership_status column
    op.drop_column('families', 'ownership_status')

