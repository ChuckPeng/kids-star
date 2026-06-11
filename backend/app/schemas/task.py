from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: str = "custom"
    difficulty: str = "required"
    category: Optional[str] = None
    base_points: int = 5
    assigned_to: List[UUID] = []
    repeat_type: str = "once"
    repeat_config: Optional[dict] = None
    due_date: Optional[str] = None
    due_time: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    base_points: Optional[int] = None
    assigned_to: Optional[List[UUID]] = None
    repeat_type: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None


class TaskResponse(BaseModel):
    id: UUID
    family_id: UUID
    title: str
    description: Optional[str] = None
    task_type: str
    difficulty: str
    category: Optional[str] = None
    base_points: int
    assigned_to: List[UUID]
    repeat_type: str
    repeat_config: Optional[dict] = None
    due_date: Optional[str] = None
    due_time: Optional[str] = None
    status: str
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class SubmissionCreate(BaseModel):
    child_note: Optional[str] = None
    photo_urls: Optional[List[str]] = None


class SubmissionReview(BaseModel):
    status: str
    parent_note: Optional[str] = None


class SubmissionResponse(BaseModel):
    id: UUID
    task_id: UUID
    child_id: UUID
    child_name: Optional[str] = None
    status: str
    child_note: Optional[str] = None
    parent_note: Optional[str] = None
    photo_urls: Optional[List[str]] = None
    points_earned: int
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Reward schemas ──

class RewardCreate(BaseModel):
    name: str
    description: Optional[str] = None
    points_cost: int
    image_url: Optional[str] = None
    stock: int = -1


class RewardResponse(BaseModel):
    id: UUID
    family_id: UUID
    name: str
    description: Optional[str] = None
    points_cost: int
    image_url: Optional[str] = None
    stock: int
    is_active: bool
    created_by: UUID
    created_at: datetime


class RedemptionCreate(BaseModel):
    reward_id: UUID


class RedemptionResponse(BaseModel):
    id: UUID
    child_id: UUID
    child_name: Optional[str] = None
    reward_id: UUID
    reward_name: Optional[str] = None
    points_spent: int
    status: str
    parent_note: Optional[str] = None
    redeemed_at: datetime
    reviewed_at: Optional[datetime] = None


# ── Application schemas ──

class RewardApplicationCreate(BaseModel):
    title: str
    description: Optional[str] = None
    photo_urls: Optional[List[str]] = None
    points_requested: int


class TaskProposalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    points_requested: int
    due_date: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: UUID
    type: str  # "reward" | "proposal"
    child_id: UUID
    child_name: Optional[str] = None
    title: str
    description: Optional[str] = None
    photo_urls: Optional[List[str]] = None
    points_requested: Optional[int] = None
    points_approved: Optional[int] = None
    status: str
    parent_note: Optional[str] = None
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None


class ApplicationReview(BaseModel):
    status: str  # "approved" | "rejected"
    parent_note: Optional[str] = None
    points_approved: Optional[int] = None


# ── Statistics schemas ──

class ChildStats(BaseModel):
    child_id: UUID
    child_name: str
    total_points: int
    required_completion_rate: float
    challenge_count: int
    approved_count: int
    rejected_count: int


class FamilyStats(BaseModel):
    children: List[ChildStats]
    total_tasks_created: int
    active_required: int
    active_challenges: int


class ManualPenalty(BaseModel):
    child_id: UUID
    amount: int
    reason: str
