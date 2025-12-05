"""Make residents.family_id nullable

Revision ID: b7f9a3c1d5e4
Revises: 204655d2e862
Create Date: 2025-12-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = 'b7f9a3c1d5e4'
down_revision: Union[str, Sequence[str], None] = '204655d2e862'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make family_id nullable so residents can be unassigned from families
    op.alter_column(
        'residents',
        'family_id',
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    # To revert to NOT NULL we must ensure no NULL values exist.
    # Create a fallback family if none exists, then assign NULLs to an existing family id.
    # Insert a fallback family only when no families exist.
    op.execute(
        """
        INSERT INTO families (family_number, family_name, created_at, updated_at)
        SELECT '0000', 'unknown', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        WHERE NOT EXISTS (SELECT 1 FROM families);
        """
    )

    # Assign any NULL family_id to an existing family (choose the first one)
    op.execute(
        """
        UPDATE residents
        SET family_id = (SELECT id FROM families LIMIT 1)
        WHERE family_id IS NULL;
        """
    )

    op.alter_column(
        'residents',
        'family_id',
        existing_type=sa.Integer(),
        nullable=False,
    )
