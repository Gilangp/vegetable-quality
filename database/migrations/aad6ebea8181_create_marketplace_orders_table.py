"""Create marketplace_orders Table

Revision ID: aad6ebea8181
Revises: 76ffe878a926
Create Date: 2025-11-30 14:33:37.638999

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aad6ebea8181'
down_revision: Union[str, Sequence[str], None] = '76ffe878a926'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "marketplace_orders",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("buyer_id", sa.Integer(), sa.ForeignKey("residents.id"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("marketplace_products.id"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("total_price", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("marketplace_orders")
