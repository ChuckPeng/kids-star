"""Challenge board - children browse and claim challenge tasks."""
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.models import User, Family, FamilyMember, Task, TaskClaim

router = APIRouter(prefix="/challenges", tags=["challenges"])


async def _get_family_member(user_id: UUID, db: AsyncSession) -> FamilyMember:
    result = await db.execute(select(FamilyMember).where(FamilyMember.user_id == user_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not in any family")
    return member


@router.get("/board")
async def list_challenge_board(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all available challenge tasks in the family's challenge board."""
    member = await _get_family_member(current_user.id, db)

    # Get all active challenge tasks in the family
    result = await db.execute(
        select(Task).where(
            Task.family_id == member.family_id,
            Task.difficulty == "challenge",
            Task.status == "active",
        ).order_by(Task.created_at.desc())
    )
    challenges = result.scalars().all()

    # Get the child's existing claims for these tasks
    claimed_task_ids: set[UUID] = set()
    if challenges:
        result = await db.execute(
            select(TaskClaim.task_id).where(
                TaskClaim.child_id == current_user.id,
                TaskClaim.task_id.in_([t.id for t in challenges]),
            )
        )
        for row in result:
            claimed_task_ids.add(row[0])

    return [
        {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "category": c.category,
            "base_points": c.base_points,
            "multiplier": c.challenge_multiplier,
            "total_points": int(c.base_points * c.challenge_multiplier),
            "due_date": str(c.due_date) if c.due_date else None,
            "due_time": str(c.due_time) if c.due_time else None,
            "claimed": c.id in claimed_task_ids,
            "created_at": c.created_at.isoformat(),
        }
        for c in challenges
    ]


@router.post("/{task_id}/claim", status_code=status.HTTP_201_CREATED)
async def claim_challenge(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Child claims a challenge task from the board."""
    member = await _get_family_member(current_user.id, db)

    # Verify the task exists, is a challenge, and belongs to this family
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.family_id == member.family_id,
            Task.difficulty == "challenge",
            Task.status == "active",
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")

    # Check if already claimed
    result = await db.execute(
        select(TaskClaim).where(
            TaskClaim.task_id == task_id,
            TaskClaim.child_id == current_user.id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already claimed this challenge")

    claim = TaskClaim(
        task_id=task_id,
        child_id=current_user.id,
    )
    db.add(claim)
    await db.flush()
    await db.refresh(claim)

    return {
        "id": claim.id,
        "task_id": str(claim.task_id),
        "status": claim.status,
        "claimed_at": claim.claimed_at.isoformat(),
    }


@router.get("/my")
async def my_challenges(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List challenges the current child has claimed."""
    member = await _get_family_member(current_user.id, db)

    result = await db.execute(
        select(TaskClaim, Task)
        .join(Task, TaskClaim.task_id == Task.id)
        .where(
            TaskClaim.child_id == current_user.id,
            Task.family_id == member.family_id,
        )
        .order_by(TaskClaim.claimed_at.desc())
    )
    rows = result.all()

    return [
        {
            "claim_id": str(claim.id),
            "claim_status": claim.status,
            "claimed_at": claim.claimed_at.isoformat(),
            "task": {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "base_points": task.base_points,
                "multiplier": task.challenge_multiplier,
                "total_points": int(task.base_points * task.challenge_multiplier),
                "due_date": str(task.due_date) if task.due_date else None,
                "due_time": str(task.due_time) if task.due_time else None,
                "status": task.status,
            }
        }
        for claim, task in rows
    ]
