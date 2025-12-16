"""Add alamat_lama and alamat_baru to family_mutations

Revision ID: e6f7a8b9c0d1
Revises: b1c2d3e4f5a6
Create Date: 2025-12-16 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = 'e6f7a8b9c0d1'
down_revision: Union[str, Sequence[str], None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns only if they don't already exist
    conn = op.get_bind()
    # check alamat_lama
    res = conn.execute(sa.text("SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'family_mutations' AND column_name = 'alamat_lama'"))
    cnt = res.scalar()
    if cnt == 0:
        op.add_column('family_mutations', sa.Column('alamat_lama', sa.Text(), nullable=True))

    # check alamat_baru
    res2 = conn.execute(sa.text("SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'family_mutations' AND column_name = 'alamat_baru'"))
    cnt2 = res2.scalar()
    if cnt2 == 0:
        op.add_column('family_mutations', sa.Column('alamat_baru', sa.Text(), nullable=True))

    # Backfill data from description where possible
    # Fetch rows as mappings so we can access by column name
    results = conn.execute(sa.text("SELECT id, description FROM family_mutations")).mappings().all()
    for row in results:
        mid = row.get('id')
        desc = row.get('description') or ''
        alamat_lama = None
        alamat_baru = None
        try:
            parts = [p.strip() for p in desc.split('|') if p.strip()]
            for p in parts:
                if p.startswith('alamat_lama:'):
                    alamat_lama = p.split(':', 1)[1].strip()
                elif p.startswith('alamat_baru:'):
                    alamat_baru = p.split(':', 1)[1].strip()
        except Exception:
            alamat_lama = None
            alamat_baru = None

        if alamat_lama is not None or alamat_baru is not None:
            conn.execute(
                sa.text(
                    "UPDATE family_mutations SET alamat_lama = :a, alamat_baru = :b WHERE id = :id"
                ),
                {"a": alamat_lama, "b": alamat_baru, "id": mid},
            )


def downgrade() -> None:
    op.drop_column('family_mutations', 'alamat_baru')
    op.drop_column('family_mutations', 'alamat_lama')
