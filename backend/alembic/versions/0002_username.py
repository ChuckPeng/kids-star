"""add username, make email optional

Revision ID: 0002_username
Revises: 0001_initial
Create Date: 2026-06-02
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0002_username'
down_revision: Union[str, None] = '0001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('username', sa.String(100), nullable=True))
    # Copy email -> username for existing users, or use 'user_' + id prefix
    op.execute("UPDATE users SET username = COALESCE(email, 'user_' || LEFT(id::text, 8)) WHERE username IS NULL")
    op.alter_column('users', 'username', nullable=False)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.alter_column('users', 'email', nullable=True)
    op.drop_index('ix_users_email')
    op.create_index('ix_users_email', 'users', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_users_username')
    op.drop_index('ix_users_email')
    op.drop_column('users', 'username')
    op.alter_column('users', 'email', nullable=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
