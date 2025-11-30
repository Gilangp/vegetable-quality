"""Create resident_approvals Table

Revision ID: 3c05748ede6e
Revises: f61ebfc68a55
Create Date: 2025-11-30 14:22:52.982413

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '3c05748ede6e'
down_revision: Union[str, Sequence[str], None] = 'f61ebfc68a55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "resident_approvals",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("resident_id", sa.Integer(), sa.ForeignKey("residents.id"), nullable=True),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("nik", sa.String(50), nullable=True),
        sa.Column("gender", sa.String(10), nullable=True),
        sa.Column("birth_place", sa.String(100), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("address", sa.Text(255), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("note", sa.Text(255), nullable=True),
        sa.Column("approved_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

def downgrade() -> None:
    op.drop_table("resident_approvals")