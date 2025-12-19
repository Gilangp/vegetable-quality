"""Create activityLogs Table

Revision ID: f61ebfc68a55
Revises: 387e0194211f
Create Date: 2025-11-30 14:21:17.619575

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = 'f61ebfc68a55'
down_revision: Union[str, Sequence[str], None] = '387e0194211f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "activity_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(100), nullable=True),
        sa.Column("description", sa.Text(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
    )

def downgrade() -> None:
    op.drop_table("activity_logs")