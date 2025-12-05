"""Add status column to houses

Revision ID: f7a1b2c3d4e5
Revises: c4d2e1f98765
Create Date: 2025-12-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = 'f7a1b2c3d4e5'
down_revision: Union[str, Sequence[str], None] = 'c4d2e1f98765'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 'status' column with default 'available' to existing houses table
    op.add_column('houses', sa.Column('status', sa.String(length=20), nullable=False, server_default=sa.text("'available'")))


def downgrade() -> None:
    op.drop_column('houses', 'status')
"""Add status column to houses

Revision ID: f7a1b2c3d4e5
Revises: c4d2e1f98765
Create Date: 2025-12-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = 'f7a1b2c3d4e5'
down_revision: Union[str, Sequence[str], None] = 'c4d2e1f98765'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add `status` column to houses with default 'available'
    op.add_column('houses', sa.Column('status', sa.String(length=20), nullable=False, server_default=sa.text("'available'")))


def downgrade() -> None:
    op.drop_column('houses', 'status')
