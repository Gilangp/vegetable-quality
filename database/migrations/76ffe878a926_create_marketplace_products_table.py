"""Create marketplace_products Table

Revision ID: 76ffe878a926
Revises: a2904c974190
Create Date: 2025-11-30 14:33:12.579115

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = '76ffe878a926'
down_revision: Union[str, Sequence[str], None] = 'a2904c974190'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "marketplace_products",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("resident_id", sa.Integer(), sa.ForeignKey("residents.id"), nullable=False),
        sa.Column("verification_id", sa.Integer(), sa.ForeignKey("verification_results.id"), nullable=True),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("price", sa.Integer(), nullable=True),
        sa.Column("stock", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(255), nullable=True),
        sa.Column("image", sa.String(100), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
    )

def downgrade() -> None:
    op.drop_table("marketplace_products")