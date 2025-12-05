"""Merge multiple heads

Revision ID: c4d2e1f98765
Revises: 9fbc27864dd3, b7f9a3c1d5e4
Create Date: 2025-12-05 10:15:00.000000

"""
from alembic import op
from typing import Sequence, Union

revision: str = 'c4d2e1f98765'
down_revision: Union[str, Sequence[str], None] = ('9fbc27864dd3', 'b7f9a3c1d5e4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Merge-only revision: no schema changes. This revision stitches two heads
    # into a single linear history so `alembic upgrade head` works.
    pass


def downgrade() -> None:
    # Downgrade would split the merge; not implemented because this revision
    # contains no schema changes.
    pass
