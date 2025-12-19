"""Drop status column from families

Revision ID: 2b4f6a9c5d7e
Revises: 08d3e5f1a2b3
Create Date: 2025-12-16 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = '2b4f6a9c5d7e'
down_revision: Union[str, Sequence[str], None] = '08d3e5f1a2b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop `status` column from families if present
    op.drop_column('families', 'status')


def downgrade() -> None:
    # Recreate the column (if rolling back)
    op.add_column('families', sa.Column('status', sa.String(length=20), nullable=False, server_default=sa.text("'vacant'")))
