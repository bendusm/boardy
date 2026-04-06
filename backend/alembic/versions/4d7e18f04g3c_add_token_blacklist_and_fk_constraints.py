"""add token blacklist table and FK constraints

Revision ID: 4d7e18f04g3c
Revises: 3c6d07e93f2b
Create Date: 2026-04-06 20:00:00.000000

Security: Adds token blacklist for logout invalidation and FK constraints for data integrity.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '4d7e18f04g3c'
down_revision: Union[str, None] = '3c6d07e93f2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create token_blacklist table for logout invalidation
    op.create_table(
        'token_blacklist',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('token_jti', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('blacklisted_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_jti'),
    )
    op.create_index('ix_token_blacklist_token_jti', 'token_blacklist', ['token_jti'])
    op.create_index('ix_token_blacklist_user_id', 'token_blacklist', ['user_id'])
    op.create_index('ix_token_blacklist_expires_at', 'token_blacklist', ['expires_at'])

    # Add FK constraints for referential integrity
    # Note: These may fail if orphaned records exist - clean up data first if needed

    # boards.owner_id -> users.id
    op.create_foreign_key(
        'fk_boards_owner_id_users',
        'boards', 'users',
        ['owner_id'], ['id'],
        ondelete='CASCADE'
    )

    # columns.board_id -> boards.id
    op.create_foreign_key(
        'fk_columns_board_id_boards',
        'columns', 'boards',
        ['board_id'], ['id'],
        ondelete='CASCADE'
    )

    # cards.board_id -> boards.id
    op.create_foreign_key(
        'fk_cards_board_id_boards',
        'cards', 'boards',
        ['board_id'], ['id'],
        ondelete='CASCADE'
    )

    # cards.column_id -> columns.id
    op.create_foreign_key(
        'fk_cards_column_id_columns',
        'cards', 'columns',
        ['column_id'], ['id'],
        ondelete='CASCADE'
    )

    # cards.assignee_id -> users.id (nullable)
    op.create_foreign_key(
        'fk_cards_assignee_id_users',
        'cards', 'users',
        ['assignee_id'], ['id'],
        ondelete='SET NULL'
    )

    # comments.card_id -> cards.id
    op.create_foreign_key(
        'fk_comments_card_id_cards',
        'comments', 'cards',
        ['card_id'], ['id'],
        ondelete='CASCADE'
    )

    # attachments.card_id -> cards.id
    op.create_foreign_key(
        'fk_attachments_card_id_cards',
        'attachments', 'cards',
        ['card_id'], ['id'],
        ondelete='CASCADE'
    )

    # board_members.board_id -> boards.id
    op.create_foreign_key(
        'fk_board_members_board_id_boards',
        'board_members', 'boards',
        ['board_id'], ['id'],
        ondelete='CASCADE'
    )

    # board_members.user_id -> users.id
    op.create_foreign_key(
        'fk_board_members_user_id_users',
        'board_members', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

    # board_invites.board_id -> boards.id
    op.create_foreign_key(
        'fk_board_invites_board_id_boards',
        'board_invites', 'boards',
        ['board_id'], ['id'],
        ondelete='CASCADE'
    )

    # board_invites.invited_by -> users.id
    op.create_foreign_key(
        'fk_board_invites_invited_by_users',
        'board_invites', 'users',
        ['invited_by'], ['id'],
        ondelete='CASCADE'
    )

    # oauth_tokens.user_id -> users.id
    op.create_foreign_key(
        'fk_oauth_tokens_user_id_users',
        'oauth_tokens', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

    # oauth_tokens.board_id -> boards.id
    op.create_foreign_key(
        'fk_oauth_tokens_board_id_boards',
        'oauth_tokens', 'boards',
        ['board_id'], ['id'],
        ondelete='CASCADE'
    )

    # oauth_auth_codes.user_id -> users.id
    op.create_foreign_key(
        'fk_oauth_auth_codes_user_id_users',
        'oauth_auth_codes', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

    # oauth_auth_codes.board_id -> boards.id
    op.create_foreign_key(
        'fk_oauth_auth_codes_board_id_boards',
        'oauth_auth_codes', 'boards',
        ['board_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Drop FK constraints
    op.drop_constraint('fk_oauth_auth_codes_board_id_boards', 'oauth_auth_codes', type_='foreignkey')
    op.drop_constraint('fk_oauth_auth_codes_user_id_users', 'oauth_auth_codes', type_='foreignkey')
    op.drop_constraint('fk_oauth_tokens_board_id_boards', 'oauth_tokens', type_='foreignkey')
    op.drop_constraint('fk_oauth_tokens_user_id_users', 'oauth_tokens', type_='foreignkey')
    op.drop_constraint('fk_board_invites_invited_by_users', 'board_invites', type_='foreignkey')
    op.drop_constraint('fk_board_invites_board_id_boards', 'board_invites', type_='foreignkey')
    op.drop_constraint('fk_board_members_user_id_users', 'board_members', type_='foreignkey')
    op.drop_constraint('fk_board_members_board_id_boards', 'board_members', type_='foreignkey')
    op.drop_constraint('fk_attachments_card_id_cards', 'attachments', type_='foreignkey')
    op.drop_constraint('fk_comments_card_id_cards', 'comments', type_='foreignkey')
    op.drop_constraint('fk_cards_assignee_id_users', 'cards', type_='foreignkey')
    op.drop_constraint('fk_cards_column_id_columns', 'cards', type_='foreignkey')
    op.drop_constraint('fk_cards_board_id_boards', 'cards', type_='foreignkey')
    op.drop_constraint('fk_columns_board_id_boards', 'columns', type_='foreignkey')
    op.drop_constraint('fk_boards_owner_id_users', 'boards', type_='foreignkey')

    # Drop token_blacklist table
    op.drop_index('ix_token_blacklist_expires_at', table_name='token_blacklist')
    op.drop_index('ix_token_blacklist_user_id', table_name='token_blacklist')
    op.drop_index('ix_token_blacklist_token_jti', table_name='token_blacklist')
    op.drop_table('token_blacklist')
