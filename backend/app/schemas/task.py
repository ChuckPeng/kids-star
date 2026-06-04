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
    due_date: Optional[str] = None
    due_time: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    base_points: Optional[int] = None
    assigned_to: Optional[List[UUID]] = None
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
    due_date: Optional[str] = None
    due_time: Optional[str] = None
    status: str
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class SubmissionCreate(BaseModel):
    child_note: Optional[str] = None


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
    points_earned: int
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
