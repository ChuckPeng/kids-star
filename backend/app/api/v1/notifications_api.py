"""Notification endpoints."""
from uuid import UUID
from typing import List, Optional
from datetime import timezone, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.models import User, FamilyMember, Notification

router = APIRouter(prefix="/notifications", tags=["notifications"])


async def _get_member(user_id: UUID, db: AsyncSession):
    result = await db.execute(select(FamilyMember).where(FamilyMember.user_id == user_id))
    m = result.scalar_one_or_none()
    if not m: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return m


@router.get("")
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    unread_only: bool = False,
    limit: int = 50,
):
    await _get_member(current_user.id, db)
    conditions = [Notification.user_id == current_user.id]
    if unread_only:
        conditions.append(Notification.is_read == False)
    result = await db.execute(
        select(Notification).where(and_(*conditions))
        .order_by(Notification.created_at.desc()).limit(limit)
    )
    return [
        {
            "id": str(n.id), "type": n.type, "title": n.title,
            "body": n.body, "is_read": n.is_read,
            "related_id": str(n.related_id) if n.related_id else None,
            "created_at": n.created_at.isoformat(),
        }
        for n in result.scalars().all()
    ]


@router.get("/unread-count")
async def unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_member(current_user.id, db)
    result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
    )
    return {"count": result.scalar() or 0}


@router.post("/{notif_id}/read")
async def mark_read(
    notif_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_member(current_user.id, db)
    result = await db.execute(
        select(Notification).where(Notification.id == notif_id, Notification.user_id == current_user.id)
    )
    n = result.scalar_one_or_none()
    if n:
        n.is_read = True
        await db.flush()
    return {"ok": True}


@router.post("/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_member(current_user.id, db)
    result = await db.execute(
        select(Notification).where(Notification.user_id == current_user.id, Notification.is_read == False)
    )
    for n in result.scalars().all():
        n.is_read = True
    await db.flush()
    return {"ok": True}
