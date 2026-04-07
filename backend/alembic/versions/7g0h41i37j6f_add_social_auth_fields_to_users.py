"""Add social auth fields to users

Revision ID: 7g0h41i37j6f
Revises: 6f9g30h26i5e_add_terms_accepted_at_to_users
Create Date: 2026-04-07 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7g0h41i37j6f'
down_revision: Union[str, None] = '6f9g30h26i5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add github_id column
    op.add_column('users', sa.Column('github_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_users_github_id'), 'users', ['github_id'], unique=True)

    # Add google_id column
    op.add_column('users', sa.Column('google_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_users_google_id'), 'users', ['google_id'], unique=True)

    # Make hashed_password nullable for social auth users
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.String(),
                    nullable=True)


def downgrade() -> None:
    # Revert hashed_password to non-nullable (will fail if social-only users exist)
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.String(),
                    nullable=False)

    # Drop google_id
    op.drop_index(op.f('ix_users_google_id'), table_name='users')
    op.drop_column('users', 'google_id')

    # Drop github_id
    op.drop_index(op.f('ix_users_github_id'), table_name='users')
    op.drop_column('users', 'github_id')
