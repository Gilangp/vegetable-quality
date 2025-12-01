"""add religion blood_type education occupation to residents

Revision ID: b1dcd08980a3
Revises: 9fbc27864dd3
Create Date: 2025-12-01 13:14:35.634810

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union


revision: str = 'b1dcd08980a3'
down_revision: Union[str, Sequence[str], None] = '9fbc27864dd3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('residents', sa.Column('religion', sa.String(50), nullable=True))
    op.add_column('residents', sa.Column('blood_type', sa.String(5), nullable=True))
    op.add_column('residents', sa.Column('education', sa.String(100), nullable=True))
    op.add_column('residents', sa.Column('occupation', sa.String(100), nullable=True))

def downgrade() -> None:
    op.drop_column('residents', 'occupation')
    op.drop_column('residents', 'education')
    op.drop_column('residents', 'blood_type')
    op.drop_column('residents', 'religion')