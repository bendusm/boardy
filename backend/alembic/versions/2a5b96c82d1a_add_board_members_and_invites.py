"""add board_members and board_invites

Revision ID: 2a5b96c82d1a
Revises: 1d4685571e9f
Create Date: 2026-04-06 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '2a5b96c82d1a'
down_revision: Union[str, None] = '1d4685571e9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create board_members table
    op.create_table(
        'board_members',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), primary_key=True),
        sa.Column('board_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('role', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='viewer'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['board_id'], ['boards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_board_members_board_id', 'board_members', ['board_id'])
    op.create_index('ix_board_members_user_id', 'board_members', ['user_id'])
    op.create_unique_constraint('uq_board_member', 'board_members', ['board_id', 'user_id'])

    # Create board_invites table
    op.create_table(
        'board_invites',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), primary_key=True),
        sa.Column('board_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('role', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='viewer'),
        sa.Column('invited_by', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default='pending'),
        sa.Column('token', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['board_id'], ['boards.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_board_invites_board_id', 'board_invites', ['board_id'])
    op.create_index('ix_board_invites_email', 'board_invites', ['email'])
    op.create_index('ix_board_invites_token', 'board_invites', ['token'], unique=True)

    # Migrate existing owners to board_members with role='owner'
    op.execute("""
        INSERT INTO board_members (id, board_id, user_id, role, created_at)
        SELECT
            CONCAT('01', UPPER(SUBSTRING(MD5(RANDOM()::TEXT), 1, 24))) as id,
            id as board_id,
            owner_id as user_id,
            'owner' as role,
            created_at
        FROM boards
    """)


def downgrade() -> None:
    op.drop_table('board_invites')
    op.drop_table('board_members')
