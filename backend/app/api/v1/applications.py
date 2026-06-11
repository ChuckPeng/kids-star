"""Child-initiated applications: reward applications + task proposals."""
from uuid import UUID
from typing import List, Optional
from datetime import date, timezone, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.models import User, FamilyMember, RewardApplication, TaskProposal, Task
from app.utils.notify import notify_application_reviewed
from app.schemas.task import (
    RewardApplicationCreate, TaskProposalCreate, ApplicationResponse, ApplicationReview,
)

router = APIRouter(prefix="/applications", tags=["applications"])


async def _get_member(user_id: UUID, db: AsyncSession) -> FamilyMember:
    result = await db.execute(select(FamilyMember).where(FamilyMember.user_id == user_id))
    m = result.scalar_one_or_none()
    if not m: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not in any family")
    return m


async def _child_name(child_id: UUID, db: AsyncSession) -> str:
    r = await db.execute(select(FamilyMember.nickname).where(FamilyMember.user_id == child_id))
    n = r.scalar_one_or_none()
    if n: return n
    r = await db.execute(select(User.name).where(User.id == child_id))
    return r.scalar_one_or_none() or "??"


# ── Submit reward application (child) ──
@router.post("/reward", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def submit_reward_app(
    data: RewardApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await _get_member(current_user.id, db)
    app = RewardApplication(
        family_id=member.family_id, child_id=current_user.id,
        title=data.title, description=data.description,
        photo_urls=data.photo_urls, points_requested=data.points_requested,
    )
    db.add(app); await db.flush(); await db.refresh(app)
    return ApplicationResponse(
        id=app.id, type="reward", child_id=app.child_id,
        child_name=await _child_name(current_user.id, db),
        title=app.title, description=app.description,
        photo_urls=app.photo_urls, points_requested=app.points_requested,
        status=app.status, submitted_at=app.submitted_at,
    )


# ── Submit task proposal (child) ──
@router.post("/proposal", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def submit_task_proposal(
    data: TaskProposalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await _get_member(current_user.id, db)
    prop = TaskProposal(
        family_id=member.family_id, child_id=current_user.id,
        title=data.title, description=data.description,
        category=data.category, points_requested=data.points_requested,
        due_date=date.fromisoformat(data.due_date) if data.due_date else None,
    )
    db.add(prop); await db.flush(); await db.refresh(prop)
    return ApplicationResponse(
        id=prop.id, type="proposal", child_id=prop.child_id,
        child_name=await _child_name(current_user.id, db),
        title=prop.title, description=prop.description,
        points_requested=prop.points_requested,
        status=prop.status, submitted_at=prop.submitted_at,
    )


# ── List all applications (parent sees family; child sees own) ──
@router.get("", response_model=List[ApplicationResponse])
async def list_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await _get_member(current_user.id, db)
    out = []
    if member.role == "parent":
        # Reward applications
        r = await db.execute(select(RewardApplication).where(RewardApplication.family_id == member.family_id).order_by(RewardApplication.submitted_at.desc()))
        for a in r.scalars().all():
            out.append(ApplicationResponse(id=a.id, type="reward", child_id=a.child_id,
                child_name=await _child_name(a.child_id, db), title=a.title, description=a.description,
                photo_urls=a.photo_urls, points_requested=a.points_requested,
                points_approved=a.points_granted, status=a.status, parent_note=a.parent_note,
                submitted_at=a.submitted_at, reviewed_at=a.reviewed_at))
        # Task proposals
        r = await db.execute(select(TaskProposal).where(TaskProposal.family_id == member.family_id).order_by(TaskProposal.submitted_at.desc()))
        for a in r.scalars().all():
            out.append(ApplicationResponse(id=a.id, type="proposal", child_id=a.child_id,
                child_name=await _child_name(a.child_id, db), title=a.title, description=a.description,
                points_requested=a.points_requested, points_approved=a.points_approved,
                status=a.status, parent_note=a.parent_note,
                submitted_at=a.submitted_at, reviewed_at=a.reviewed_at))
    else:
        r = await db.execute(select(RewardApplication).where(RewardApplication.child_id == current_user.id).order_by(RewardApplication.submitted_at.desc()))
        for a in r.scalars().all():
            out.append(ApplicationResponse(id=a.id, type="reward", child_id=a.child_id,
                child_name=current_user.name, title=a.title, description=a.description,
                photo_urls=a.photo_urls, points_requested=a.points_requested,
                points_approved=a.points_granted, status=a.status, parent_note=a.parent_note,
                submitted_at=a.submitted_at, reviewed_at=a.reviewed_at))
        r = await db.execute(select(TaskProposal).where(TaskProposal.child_id == current_user.id).order_by(TaskProposal.submitted_at.desc()))
        for a in r.scalars().all():
            out.append(ApplicationResponse(id=a.id, type="proposal", child_id=a.child_id,
                child_name=current_user.name, title=a.title, description=a.description,
                points_requested=a.points_requested, points_approved=a.points_approved,
                status=a.status, parent_note=a.parent_note,
                submitted_at=a.submitted_at, reviewed_at=a.reviewed_at))
    return out


# ── Review application (parent) ──
@router.post("/{app_id}/review", response_model=ApplicationResponse)
async def review_application(
    app_id: UUID, data: ApplicationReview,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await _get_member(current_user.id, db)
    if member.role not in ("parent",): raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    # Try reward application first, then task proposal
    r = await db.execute(select(RewardApplication).where(RewardApplication.id == app_id, RewardApplication.family_id == member.family_id))
    reward_app = r.scalar_one_or_none()
    if reward_app:
        reward_app.status = data.status
        reward_app.parent_note = data.parent_note
        reward_app.reviewed_by = current_user.id
        reward_app.reviewed_at = datetime.now(timezone.utc)
        if data.status == "approved":
            pts = data.points_approved or reward_app.points_requested
            reward_app.points_granted = pts
            r2 = await db.execute(select(FamilyMember).where(FamilyMember.family_id == member.family_id, FamilyMember.user_id == reward_app.child_id))
            cm = r2.scalar_one_or_none()
            if cm: cm.points += pts
        await notify_application_reviewed(db, reward_app.child_id, reward_app.title, data.status)
        await db.flush(); await db.refresh(reward_app)
        return ApplicationResponse(id=reward_app.id, type="reward", child_id=reward_app.child_id,
            child_name=await _child_name(reward_app.child_id, db),
            title=reward_app.title, description=reward_app.description,
            photo_urls=reward_app.photo_urls,
            points_requested=reward_app.points_requested,
            points_approved=reward_app.points_granted,
            status=reward_app.status, parent_note=reward_app.parent_note,
            submitted_at=reward_app.submitted_at, reviewed_at=reward_app.reviewed_at)

    r = await db.execute(select(TaskProposal).where(TaskProposal.id == app_id, TaskProposal.family_id == member.family_id))
    prop = r.scalar_one_or_none()
    if not prop: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    prop.status = data.status
    prop.parent_note = data.parent_note
    prop.reviewed_by = current_user.id
    prop.reviewed_at = datetime.now(timezone.utc)
    if data.status == "approved":
        pts = data.points_approved or prop.points_requested
        prop.points_approved = pts
        await notify_application_reviewed(db, prop.child_id, prop.title, data.status)
        # Auto-create challenge task
        task = Task(
            family_id=member.family_id, title=prop.title,
            description=prop.description, difficulty="challenge",
            category=prop.category, base_points=pts,
            assigned_to=[prop.child_id],
            repeat_type="once", created_by=current_user.id,
        )
        db.add(task)
        await db.flush()
        prop.created_task_id = task.id
    await db.flush(); await db.refresh(prop)
    return ApplicationResponse(id=prop.id, type="proposal", child_id=prop.child_id,
        child_name=await _child_name(prop.child_id, db),
        title=prop.title, description=prop.description,
        points_requested=prop.points_requested,
        points_approved=prop.points_approved,
        status=prop.status, parent_note=prop.parent_note,
        submitted_at=prop.submitted_at, reviewed_at=prop.reviewed_at)

