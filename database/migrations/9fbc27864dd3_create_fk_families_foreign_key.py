"""Create fk_families foreign_key

Revision ID: 9fbc27864dd3
Revises: af61cd517646
Create Date: 2025-11-30 14:58:33.593817

"""
from alembic import op
from typing import Sequence, Union

revision: str = '9fbc27864dd3'
down_revision: Union[str, Sequence[str], None] = 'af61cd517646'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_foreign_key(
        "fk_families_head_resident_id",
        "families",
        "residents",
        ["head_resident_id"],
        ["id"],
        ondelete="SET NULL" 
    )

def downgrade() -> None:
    op.drop_constraint("fk_families_head_resident_id", "families", type_="foreignkey")