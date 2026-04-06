"""add rate_limit_entries table

Revision ID: 5e8f29g15h4d
Revises: 4d7e18f04g3c
Create Date: 2026-04-06 22:00:00.000000

Security: PostgreSQL-based rate limiting for multi-worker deployments.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '5e8f29g15h4d'
down_revision: Union[str, None] = '4d7e18f04g3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create rate_limit_entries table for PostgreSQL-based rate limiting
    op.create_table(
        'rate_limit_entries',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('key', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_rate_limit_entries_key', 'rate_limit_entries', ['key'])
    op.create_index('ix_rate_limit_entries_created_at', 'rate_limit_entries', ['created_at'])
    # Composite index for efficient cleanup queries
    op.create_index(
        'ix_rate_limit_entries_key_created_at',
        'rate_limit_entries',
        ['key', 'created_at']
    )


def downgrade() -> None:
    op.drop_index('ix_rate_limit_entries_key_created_at', table_name='rate_limit_entries')
    op.drop_index('ix_rate_limit_entries_created_at', table_name='rate_limit_entries')
    op.drop_index('ix_rate_limit_entries_key', table_name='rate_limit_entries')
    op.drop_table('rate_limit_entries')
