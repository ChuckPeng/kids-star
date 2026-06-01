import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import String, Integer, Boolean, Text, Float, Date, Time, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="parent")  # parent | child | admin
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    family_memberships: Mapped[list["FamilyMember"]] = relationship(back_populates="user")
    created_tasks: Mapped[list["Task"]] = relationship(foreign_keys="Task.created_by", back_populates="creator")
    submissions: Mapped[list["Submission"]] = relationship(foreign_keys="Submission.child_id", back_populates="child")
    reviewed_submissions: Mapped[list["Submission"]] = relationship(foreign_keys="Submission.reviewed_by")


class Family(Base):
    __tablename__ = "families"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    invite_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    max_daily_penalty: Mapped[int] = mapped_column(Integer, default=20)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    members: Mapped[list["FamilyMember"]] = relationship(back_populates="family")
    tasks: Mapped[list["Task"]] = relationship(back_populates="family")
    rewards: Mapped[list["Reward"]] = relationship(back_populates="family")
    badges: Mapped[list["Badge"]] = relationship(back_populates="family")
    penalty_rules: Mapped[list["FamilyPenaltyRule"]] = relationship(back_populates="family")


class FamilyMember(Base):
    __tablename__ = "family_members"
    __table_args__ = (UniqueConstraint("user_id", "family_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="child")  # parent | child
    nickname: Mapped[Optional[str]] = mapped_column(String(50))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    points: Mapped[int] = mapped_column(Integer, default=0)
    joined_at: Mapped[datetime] = mapped_column(default=utcnow)

    user: Mapped["User"] = relationship(back_populates="family_memberships")
    family: Mapped["Family"] = relationship(back_populates="members")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    task_type: Mapped[str] = mapped_column(String(30), nullable=False, default="custom")  # daily_habit | homework | chore | custom
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="required")  # required | challenge
    category: Mapped[Optional[str]] = mapped_column(String(50))
    base_points: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    challenge_multiplier: Mapped[float] = mapped_column(Float, default=1.5)
    bonus_points: Mapped[int] = mapped_column(Integer, default=0)
    penalty_points: Mapped[int] = mapped_column(Integer, default=0)
    allow_overtime_discount: Mapped[bool] = mapped_column(Boolean, default=True)
    repeat_type: Mapped[str] = mapped_column(String(20), default="once")  # once | daily | weekly | monthly
    repeat_config: Mapped[Optional[dict]] = mapped_column(JSONB)
    due_date: Mapped[Optional[datetime]] = mapped_column(Date)
    due_time: Mapped[Optional[datetime]] = mapped_column(Time)
    assigned_to: Mapped[list[uuid.UUID]] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=False, default=[])
    claim_limit: Mapped[int] = mapped_column(Integer, default=0)
    claim_deadline_hours: Mapped[int] = mapped_column(Integer, default=48)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active | paused | completed | cancelled
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    family: Mapped["Family"] = relationship(back_populates="tasks")
    creator: Mapped["User"] = relationship(foreign_keys=[created_by], back_populates="created_tasks")
    submissions: Mapped[list["Submission"]] = relationship(back_populates="task")
    claims: Mapped[list["TaskClaim"]] = relationship(back_populates="task")


class TaskClaim(Base):
    __tablename__ = "task_claims"
    __table_args__ = (UniqueConstraint("task_id", "child_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    child_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="claimed")  # claimed | in_progress | completed | abandoned
    claimed_at: Mapped[datetime] = mapped_column(default=utcnow)
    completed_at: Mapped[Optional[datetime]]

    task: Mapped["Task"] = relationship(back_populates="claims")


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    child_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | approved | rejected
    photo_urls: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    child_note: Mapped[Optional[str]] = mapped_column(Text)
    parent_note: Mapped[Optional[str]] = mapped_column(Text)
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    submitted_at: Mapped[datetime] = mapped_column(default=utcnow)
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at: Mapped[Optional[datetime]]

    task: Mapped["Task"] = relationship(back_populates="submissions")
    child: Mapped["User"] = relationship(foreign_keys=[child_id], back_populates="submissions")
    reviewer: Mapped[Optional["User"]] = relationship(foreign_keys=[reviewed_by], back_populates="reviewed_submissions")


class PointsRecord(Base):
    __tablename__ = "points_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # task_complete | bonus | auto_penalty | manual_penalty | redemption | reward_application | manual
    reason: Mapped[Optional[str]] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class Reward(Base):
    __tablename__ = "rewards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    points_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    stock: Mapped[int] = mapped_column(Integer, default=-1)  # -1 = unlimited
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    family: Mapped["Family"] = relationship(back_populates="rewards")
    redemptions: Mapped[list["Redemption"]] = relationship(back_populates="reward")


class Redemption(Base):
    __tablename__ = "redemptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reward_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rewards.id"), nullable=False)
    points_spent: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | approved | fulfilled | rejected
    parent_note: Mapped[Optional[str]] = mapped_column(Text)
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    redeemed_at: Mapped[datetime] = mapped_column(default=utcnow)
    reviewed_at: Mapped[Optional[datetime]]
    fulfilled_at: Mapped[Optional[datetime]]

    reward: Mapped["Reward"] = relationship(back_populates="redemptions")


class Badge(Base):
    __tablename__ = "badges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    icon_url: Mapped[Optional[str]] = mapped_column(String(500))
    condition: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    family: Mapped["Family"] = relationship(back_populates="badges")


class ChildBadge(Base):
    __tablename__ = "child_badges"
    __table_args__ = (UniqueConstraint("child_id", "badge_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    badge_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("badges.id"), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(default=utcnow)


class FamilyPenaltyRule(Base):
    __tablename__ = "family_penalty_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(30), nullable=False)  # streak_penalty | weekly_completion | challenge_abuse
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    trigger_config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    penalty_action: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    family: Mapped["Family"] = relationship(back_populates="penalty_rules")


class RewardApplication(Base):
    __tablename__ = "reward_applications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    child_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    photo_urls: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    points_requested: Mapped[int] = mapped_column(Integer, nullable=False)
    points_granted: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | approved | rejected
    parent_note: Mapped[Optional[str]] = mapped_column(Text)
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    submitted_at: Mapped[datetime] = mapped_column(default=utcnow)
    reviewed_at: Mapped[Optional[datetime]]


class TaskProposal(Base):
    __tablename__ = "task_proposals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    child_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    points_requested: Mapped[int] = mapped_column(Integer, nullable=False)
    points_approved: Mapped[Optional[int]] = mapped_column(Integer)
    multiplier_approved: Mapped[float] = mapped_column(Float, default=1.5)
    due_date: Mapped[Optional[datetime]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | approved | rejected
    parent_note: Mapped[Optional[str]] = mapped_column(Text)
    created_task_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    submitted_at: Mapped[datetime] = mapped_column(default=utcnow)
    reviewed_at: Mapped[Optional[datetime]]


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("idx_notifications_user_unread", "user_id", "is_read", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)  # new_task | challenge_new | review_result | redemption_update | penalty | reminder
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    related_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
