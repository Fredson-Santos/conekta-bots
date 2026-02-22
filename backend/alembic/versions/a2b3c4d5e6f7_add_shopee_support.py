"""add_shopee_support

Revision ID: a2b3c4d5e6f7
Revises: f21c30f30def
Create Date: 2026-02-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2b3c4d5e6f7'
down_revision: Union[str, None] = 'f21c30f30def'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tabela configuracao (if_not_exists para ambientes onde já foi criada via metadata)
    op.execute("""
        CREATE TABLE IF NOT EXISTS configuracao (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            shopee_app_id VARCHAR(100),
            shopee_app_secret VARCHAR(200),
            owner_id INTEGER NOT NULL UNIQUE,
            FOREIGN KEY(owner_id) REFERENCES user (id)
        )
    """)

    # Adicionar converter_shopee à tabela regra
    with op.batch_alter_table('regra', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('converter_shopee', sa.Boolean(), nullable=False, server_default=sa.text('0'))
        )


def downgrade() -> None:
    with op.batch_alter_table('regra', schema=None) as batch_op:
        batch_op.drop_column('converter_shopee')

    op.drop_table('configuracao')
