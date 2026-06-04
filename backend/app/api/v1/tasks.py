from uuid import UUID
from typing import Optional, List
from datetime import date, time, timezone, datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models.models import User, Family, FamilyMember, Task, Submission
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, SubmissionCreate, SubmissionReview, SubmissionResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


async def _get_family_member(user_id: UUID, db: AsyncSession) -> FamilyMember:
    result = await db.execute(select(FamilyMember).where(FamilyMember.user_id == user_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not in any family")
    return member


async def _require_parent(current_user: User, db: AsyncSession) -> FamilyMember:
    member = await _get_family_member(current_user.id, db)
    if member.role not in ("parent",):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Parent access required")
    return member


async def _require_member(current_user: User, db: AsyncSession) -> FamilyMember:
    return await _get_family_member(current_user.id, db)


async def _get_child_name(child_id: UUID, db: AsyncSession) -> str:
    result = await db.execute(select(User.name).where(User.id == child_id))
    name = result.scalar_one_or_none()
    # Also check family_member nickname
    result2 = await db.execute(
        select(FamilyMember.nickname).where(FamilyMember.user_id == child_id)
    )
    nickname = result2.scalar_one_or_none()
    return nickname or name or "未知"


def _task_to_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        family_id=task.family_id,
        title=task.title,
        description=task.description,
        task_type=task.task_type,
        difficulty=task.difficulty,
        category=task.category,
        base_points=task.base_points,
        assigned_to=task.assigned_to or [],
        repeat_type=task.repeat_type,
        due_date=str(task.due_date) if task.due_date else None,
        due_time=str(task.due_time) if task.due_time else None,
        status=task.status,
        created_by=task.created_by,
        created_at=task.created_at,
    )


# ── Create Task (parent) ──
@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await _require_parent(current_user, db)

    task = Task(
        family_id=member.family_id,
        title=data.title,
        description=data.description,
        task_type=data.task_type,
        difficulty=data.difficulty,
        category=data.category,
        base_points=data.base_points,
        assigned_to=data.assigned_to,
        repeat_type=data.repeat_type,
        due_date=date.fromisoformat(data.due_date) if data.due_date else None,
        due_time=time.fromisoformat(data.due_time) if data.due_time else None,
        created_by=current_user.id,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return _task_to_response(task)


# ── List Tasks ──
@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    difficulty: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    member = await _require_member(current_user, db)

    conditions = [Task.family_id == member.family_id]
    if difficulty:
        conditions.append(Task.difficulty == difficulty)
    if status_filter:
        conditions.append(Task.status == status_filter)

    # Child sees only tasks assigned to them or challenge tasks
    if member.role == "child":
        conditions.append(
            and_(
                Task.status == "active",
                (Task.assigned_to.contains([current_user.id])) | (Task.difficulty == "challenge")
            )
        )

    result = await db.execute(
        select(Task).where(and_(*conditions)).order_by(Task.created_at.desc())
    )
    tasks = result.scalars().all()
    return [_task_to_response(t) for t in tasks]


# ── Update Task (parent) ──
@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await _require_parent(current_user, db)

    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.family_id == member.family_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.base_points is not None:
        task.base_points = data.base_points
    if data.assigned_to is not None:
        task.assigned_to = data.assigned_to
    if data.status is not None:
        task.status = data.status
    if data.due_date is not None:
        task.due_date = date.fromisoformat(data.due_date) if data.due_date else None

    await db.flush()
    await db.refresh(task)
    return _task_to_response(task)


# ── Submit Task (child) ──
@router.post("/{task_id}/submit", response_model=SubmissionResponse)
async def submit_task(
    task_id: UUID,
    data: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await _require_member(current_user, db)

    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.family_id == member.family_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Check already submitted (pending or approved today)
    today = date.today()
    existing = await db.execute(
        select(Submission).where(
            Submission.task_id == task_id,
            Submission.child_id == current_user.id,
            or_(
                Submission.status == "pending",
                and_(
                    Submission.status == "approved",
                    Submission.submitted_at >= today,
                ),
            ),
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already submitted, awaiting review or already approved today")

    submission = Submission(
        task_id=task_id,
        child_id=current_user.id,
        child_note=data.child_note,
    )
    db.add(submission)
    await db.flush()
    await db.refresh(submission)
    return SubmissionResponse(
        id=submission.id,
        task_id=submission.task_id,
        child_id=submission.child_id,
        child_name=current_user.name,
        status=submission.status,
        child_note=submission.child_note,
        parent_note=submission.parent_note,
        points_earned=submission.points_earned,
        submitted_at=submission.submitted_at,
        reviewed_at=submission.reviewed_at,
    )


# ── Review Submission (parent) ──
@router.post("/{task_id}/review", response_model=SubmissionResponse)
async def review_submission(
    task_id: UUID,
    data: SubmissionReview,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await _require_parent(current_user, db)

    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.family_id == member.family_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Find latest pending submission for this task
    result = await db.execute(
        select(Submission)
        .where(Submission.task_id == task_id, Submission.status == "pending")
        .order_by(Submission.submitted_at.desc())
        .limit(1)
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No pending submission")

    child_name = await _get_child_name(submission.child_id, db)

    submission.status = data.status
    submission.parent_note = data.parent_note
    submission.reviewed_by = current_user.id
    submission.reviewed_at = datetime.now(timezone.utc)

    if data.status == "approved":
        multiplier = task.challenge_multiplier if task.difficulty == "challenge" else 1.0
        submission.points_earned = int(task.base_points * multiplier)
        result = await db.execute(
            select(FamilyMember).where(
                FamilyMember.family_id == member.family_id,
                FamilyMember.user_id == submission.child_id,
            )
        )
        child_member = result.scalar_one_or_none()
        if child_member:
            child_member.points += submission.points_earned

    await db.flush()
    await db.refresh(submission)
    return SubmissionResponse(
        id=submission.id,
        task_id=submission.task_id,
        child_id=submission.child_id,
        child_name=child_name,
        status=submission.status,
        child_note=submission.child_note,
        parent_note=submission.parent_note,
        points_earned=submission.points_earned,
        submitted_at=submission.submitted_at,
        reviewed_at=submission.reviewed_at,
    )


# ── Get submissions for a task ──
@router.get("/{task_id}/submissions", response_model=List[SubmissionResponse])
async def get_submissions(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await _require_member(current_user, db)

    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.family_id == member.family_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Join with users and family_members to get child names
    result = await db.execute(
        select(Submission, User.name, FamilyMember.nickname)
        .join(User, Submission.child_id == User.id, isouter=True)
        .join(FamilyMember, and_(
            FamilyMember.user_id == Submission.child_id,
            FamilyMember.family_id == member.family_id,
        ), isouter=True)
        .where(Submission.task_id == task_id)
        .order_by(Submission.submitted_at.desc())
    )
    rows = result.all()
    return [
        SubmissionResponse(
            id=s.id, task_id=s.task_id, child_id=s.child_id,
            child_name=nickname or name or "未知",
            status=s.status, child_note=s.child_note, parent_note=s.parent_note,
            points_earned=s.points_earned, submitted_at=s.submitted_at,
            reviewed_at=s.reviewed_at,
        )
        for s, name, nickname in rows
    ]


# ── Get my submissions status (child) ──
@router.get("/my-submissions", response_model=List[SubmissionResponse])
async def get_my_submissions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await _require_member(current_user, db)

    result = await db.execute(
        select(Submission)
        .where(Submission.child_id == current_user.id)
        .order_by(Submission.submitted_at.desc())
        .limit(50)
    )
    submissions = result.scalars().all()
    return [
        SubmissionResponse(
            id=s.id, task_id=s.task_id, child_id=s.child_id,
            child_name=current_user.name,
            status=s.status, child_note=s.child_note, parent_note=s.parent_note,
            points_earned=s.points_earned, submitted_at=s.submitted_at,
            reviewed_at=s.reviewed_at,
        )
        for s in submissions
    ]
