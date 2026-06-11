"""Family statistics and manual penalty."""
from uuid import UUID
from typing import List
from datetime import date, timezone, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.models import User, FamilyMember, Task, Submission, PointsRecord
from app.schemas.task import FamilyStats, ChildStats, ManualPenalty

router = APIRouter(prefix="/stats", tags=["stats"])


async def _get_member(user_id: UUID, db: AsyncSession) -> FamilyMember:
    result = await db.execute(select(FamilyMember).where(FamilyMember.user_id == user_id))
    m = result.scalar_one_or_none()
    if not m: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not in any family")
    return m


@router.get("/family", response_model=FamilyStats)
async def family_stats(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    member = await _get_member(current_user.id, db)

    # Children stats
    children = await db.execute(
        select(FamilyMember).where(FamilyMember.family_id == member.family_id, FamilyMember.role == "child")
    )
    child_stats = []
    for c in children.scalars().all():
        child_name = c.nickname or (await db.execute(select(User.name).where(User.id == c.user_id))).scalar_one_or_none() or "??"
        # Required task completion
        required_tasks = await db.execute(select(func.count(Task.id)).where(
            Task.family_id == member.family_id, Task.difficulty == "required",
            Task.assigned_to.contains([c.user_id])
        ))
        total_required = required_tasks.scalar() or 0
        approved = await db.execute(select(func.count(Submission.id)).where(
            Submission.child_id == c.user_id, Submission.status == "approved"
        ))
        approved_count = approved.scalar() or 0
        rejected = await db.execute(select(func.count(Submission.id)).where(
            Submission.child_id == c.user_id, Submission.status == "rejected"
        ))
        rejected_count = rejected.scalar() or 0
        challenges = await db.execute(select(func.count(Submission.id)).where(
            Submission.child_id == c.user_id,
        ))
        challenge_count = challenges.scalar() or 0
        rate = round(approved_count / max(total_required, 1) * 100, 1)

        child_stats.append(ChildStats(
            child_id=c.user_id, child_name=child_name,
            total_points=c.points,
            required_completion_rate=rate,
            challenge_count=challenge_count,
            approved_count=approved_count,
            rejected_count=rejected_count,
        ))

    # Task counts
    total_created = (await db.execute(select(func.count(Task.id)).where(Task.family_id == member.family_id))).scalar() or 0
    active_required = (await db.execute(select(func.count(Task.id)).where(
        Task.family_id == member.family_id, Task.difficulty == "required", Task.status == "active"
    ))).scalar() or 0
    active_challenges = (await db.execute(select(func.count(Task.id)).where(
        Task.family_id == member.family_id, Task.difficulty == "challenge", Task.status == "active"
    ))).scalar() or 0

    return FamilyStats(
        children=child_stats, total_tasks_created=total_created,
        active_required=active_required, active_challenges=active_challenges,
    )


# ── Manual penalty (parent deducts points) ──
@router.post("/penalty")
async def manual_penalty(
    data: ManualPenalty,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await _get_member(current_user.id, db)
    if member.role not in ("parent",): raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if data.amount <= 0: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")

    child = await db.execute(select(FamilyMember).where(
        FamilyMember.family_id == member.family_id,
        FamilyMember.user_id == data.child_id,
        FamilyMember.role == "child",
    ))
    cm = child.scalar_one_or_none()
    if not cm: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")
    cm.points = max(0, cm.points - data.amount)

    record = PointsRecord(child_id=data.child_id, amount=-data.amount, type="manual_penalty", reason=data.reason)
    db.add(record)
    await db.flush()
    return {"ok": True, "new_points": cm.points}
