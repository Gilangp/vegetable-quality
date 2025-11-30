"""Create users Table

Revision ID: 387e0194211f
Revises: 204655d2e862
Create Date: 2025-11-30 14:09:42.626078

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = '387e0194211f'
down_revision: Union[str, Sequence[str], None] = '204655d2e862'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("resident_id", sa.Integer(), sa.ForeignKey("residents.id"), nullable=True),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("password", sa.String(100), nullable=True),
        sa.Column("role", sa.String(50), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("email", sa.String(100), nullable=True),
        sa.Column("avatar", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )

def downgrade() -> None:
    op.drop_table("users")