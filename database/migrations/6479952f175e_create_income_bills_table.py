"""Create income_bills Table

Revision ID: 6479952f175e
Revises: 6ec985b81b4d
Create Date: 2025-11-30 14:28:53.031336

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6479952f175e'
down_revision: Union[str, Sequence[str], None] = '6ec985b81b4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "income_bills",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("resident_id", sa.Integer(), sa.ForeignKey("residents.id"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("income_categories.id"), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("income_bills")
