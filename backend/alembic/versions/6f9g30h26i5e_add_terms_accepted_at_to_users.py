"""add terms_accepted_at to users

Revision ID: 6f9g30h26i5e
Revises: 5e8f29g15h4d
Create Date: 2026-04-07 12:00:00.000000

GDPR: Track when users accepted Terms of Service and Privacy Policy.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f9g30h26i5e'
down_revision: Union[str, None] = '5e8f29g15h4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add terms_accepted_at column to users table
    op.add_column(
        'users',
        sa.Column('terms_accepted_at', sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('users', 'terms_accepted_at')
