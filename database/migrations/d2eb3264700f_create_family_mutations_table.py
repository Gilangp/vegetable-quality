"""Create family_mutations Table

Revision ID: d2eb3264700f
Revises: 3c05748ede6e
Create Date: 2025-11-30 14:24:14.544381

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = 'd2eb3264700f'
down_revision: Union[str, Sequence[str], None] = '3c05748ede6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "family_mutations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("family_id", sa.Integer(), sa.ForeignKey("families.id"), nullable=False),
        sa.Column("mutation_type", sa.String(100), nullable=True),
        sa.Column("description", sa.Text(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
    )

def downgrade() -> None:
    op.drop_table("family_mutations")