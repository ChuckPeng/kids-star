"""initial schema with username login

Revision ID: 0001_username
Revises:
Create Date: 2026-06-02
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0001_username'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, server_default='parent'),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table('families',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('invite_code', sa.String(20), nullable=False),
        sa.Column('max_daily_penalty', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invite_code'),
    )
    op.create_index('ix_families_invite_code', 'families', ['invite_code'])

    op.create_table('family_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, server_default='child'),
        sa.Column('nickname', sa.String(50), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['family_id'], ['families.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'family_id'),
    )

    op.create_table('tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('task_type', sa.String(30), nullable=False, server_default='custom'),
        sa.Column('difficulty', sa.String(20), nullable=False, server_default='required'),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('base_points', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('challenge_multiplier', sa.Float(), nullable=False, server_default='1.5'),
        sa.Column('bonus_points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('penalty_points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('allow_overtime_discount', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('repeat_type', sa.String(20), nullable=False, server_default='once'),
        sa.Column('repeat_config', postgresql.JSONB(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('due_time', sa.Time(), nullable=True),
        sa.Column('assigned_to', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False, server_default='{}'),
        sa.Column('claim_limit', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('claim_deadline_hours', sa.Integer(), nullable=False, server_default='48'),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['family_id'], ['families.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('task_claims',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('child_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='claimed'),
        sa.Column('claimed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['child_id'], ['users.id']),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id', 'child_id'),
    )

    op.create_table('submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('child_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('photo_urls', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('child_note', sa.Text(), nullable=True),
        sa.Column('parent_note', sa.Text(), nullable=True),
        sa.Column('points_earned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['child_id'], ['users.id']),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id']),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('points_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('child_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('reason', sa.String(300), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['child_id'], ['users.id']),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('rewards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('points_cost', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('stock', sa.Integer(), nullable=False, server_default='-1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['family_id'], ['families.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('redemptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('child_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reward_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('points_spent', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('parent_note', sa.Text(), nullable=True),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('redeemed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fulfilled_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['child_id'], ['users.id']),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id']),
        sa.ForeignKeyConstraint(['reward_id'], ['rewards.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('badges',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon_url', sa.String(500), nullable=True),
        sa.Column('condition', postgresql.JSONB(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['family_id'], ['families.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('child_badges',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('child_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('badge_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('earned_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['badge_id'], ['badges.id']),
        sa.ForeignKeyConstraint(['child_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('child_id', 'badge_id'),
    )

    op.create_table('family_penalty_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rule_type', sa.String(30), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('trigger_config', postgresql.JSONB(), nullable=False),
        sa.Column('penalty_action', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['family_id'], ['families.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('reward_applications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('child_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('photo_urls', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('points_requested', sa.Integer(), nullable=False),
        sa.Column('points_granted', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('parent_note', sa.Text(), nullable=True),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['child_id'], ['users.id']),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id']),
        sa.ForeignKeyConstraint(['family_id'], ['families.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('task_proposals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('child_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('points_requested', sa.Integer(), nullable=False),
        sa.Column('points_approved', sa.Integer(), nullable=True),
        sa.Column('multiplier_approved', sa.Float(), nullable=False, server_default='1.5'),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('parent_note', sa.Text(), nullable=True),
        sa.Column('created_task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['child_id'], ['users.id']),
        sa.ForeignKeyConstraint(['created_task_id'], ['tasks.id']),
        sa.ForeignKeyConstraint(['family_id'], ['families.id']),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(30), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('related_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_notifications_user_unread', 'notifications', ['user_id', 'is_read', 'created_at'])


def downgrade() -> None:
    op.drop_index('idx_notifications_user_unread')
    op.drop_table('notifications')
    op.drop_table('task_proposals')
    op.drop_table('reward_applications')
    op.drop_table('family_penalty_rules')
    op.drop_table('child_badges')
    op.drop_table('badges')
    op.drop_table('redemptions')
    op.drop_table('rewards')
    op.drop_table('points_records')
    op.drop_table('submissions')
    op.drop_table('task_claims')
    op.drop_table('tasks')
    op.drop_table('family_members')
    op.drop_table('families')
    op.drop_index('ix_users_email')
    op.drop_index('ix_users_username')
    op.drop_table('users')
