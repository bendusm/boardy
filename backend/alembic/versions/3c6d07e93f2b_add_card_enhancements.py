"""add card enhancements: color, assignee, due_date, labels, archived

Revision ID: 3c6d07e93f2b
Revises: 2a5b96c82d1a
Create Date: 2026-04-06 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '3c6d07e93f2b'
down_revision: Union[str, None] = '2a5b96c82d1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add name field to users
    op.add_column('users', sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True))

    # Add new fields to cards
    op.add_column('cards', sa.Column('color', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='gray'))
    op.add_column('cards', sa.Column('assignee_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('cards', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('cards', sa.Column('labels', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('cards', sa.Column('archived', sa.Boolean(), nullable=False, server_default='false'))

    # Add index for assignee_id
    op.create_index('ix_cards_assignee_id', 'cards', ['assignee_id'])


def downgrade() -> None:
    op.drop_index('ix_cards_assignee_id', table_name='cards')
    op.drop_column('cards', 'archived')
    op.drop_column('cards', 'labels')
    op.drop_column('cards', 'due_date')
    op.drop_column('cards', 'assignee_id')
    op.drop_column('cards', 'color')
    op.drop_column('users', 'name')
