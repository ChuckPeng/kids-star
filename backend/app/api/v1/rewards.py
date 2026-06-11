"""Reward shop - parent manages rewards, children redeem."""
from uuid import UUID
from typing import List, Optional
from datetime import timezone, datetime

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.models import User, FamilyMember, Reward, Redemption
from app.schemas.task import RewardCreate, RewardResponse, RedemptionResponse

router = APIRouter(prefix="/rewards", tags=["rewards"])


async def _get_member(user_id: UUID, db: AsyncSession) -> FamilyMember:
    result = await db.execute(select(FamilyMember).where(FamilyMember.user_id == user_id))
    m = result.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not in any family")
    return m


async def _child_name(child_id: UUID, db: AsyncSession) -> str:
    r = await db.execute(select(FamilyMember.nickname).where(FamilyMember.user_id == child_id))
    n = r.scalar_one_or_none()
    if n: return n
    r = await db.execute(select(User.name).where(User.id == child_id))
    return r.scalar_one_or_none() or "??"


@router.get("", response_model=List[RewardResponse])
async def list_rewards(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    member = await _get_member(current_user.id, db)
    result = await db.execute(
        select(Reward).where(Reward.family_id == member.family_id, Reward.is_active == True)
        .order_by(Reward.points_cost.asc())
    )
    return [RewardResponse(id=r.id, family_id=r.family_id, name=r.name, description=r.description,
            points_cost=r.points_cost, image_url=r.image_url, stock=r.stock,
            is_active=r.is_active, created_by=r.created_by, created_at=r.created_at)
            for r in result.scalars().all()]


@router.post("", response_model=RewardResponse, status_code=status.HTTP_201_CREATED)
async def create_reward(data: RewardCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    member = await _get_member(current_user.id, db)
    if member.role not in ("parent",): raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Parent only")
    r = Reward(family_id=member.family_id, name=data.name, description=data.description,
               points_cost=data.points_cost, image_url=data.image_url, stock=data.stock, created_by=current_user.id)
    db.add(r); await db.flush(); await db.refresh(r)
    return RewardResponse(id=r.id, family_id=r.family_id, name=r.name, description=r.description,
            points_cost=r.points_cost, image_url=r.image_url, stock=r.stock,
            is_active=r.is_active, created_by=r.created_by, created_at=r.created_at)


@router.patch("/{reward_id}", response_model=RewardResponse)
async def update_reward(reward_id: UUID, data: RewardCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    member = await _get_member(current_user.id, db)
    if member.role not in ("parent",): raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    result = await db.execute(select(Reward).where(Reward.id == reward_id, Reward.family_id == member.family_id))
    r = result.scalar_one_or_none()
    if not r: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    for f in ("name","description","points_cost","image_url","stock"): setattr(r, f, getattr(data, f))
    await db.flush(); await db.refresh(r)
    return RewardResponse(id=r.id, family_id=r.family_id, name=r.name, description=r.description,
            points_cost=r.points_cost, image_url=r.image_url, stock=r.stock,
            is_active=r.is_active, created_by=r.created_by, created_at=r.created_at)


@router.delete("/{reward_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reward(reward_id: UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    member = await _get_member(current_user.id, db)
    if member.role not in ("parent",): raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    result = await db.execute(select(Reward).where(Reward.id == reward_id, Reward.family_id == member.family_id))
    r = result.scalar_one_or_none()
    if not r: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    r.is_active = False; await db.flush()


@router.post("/{reward_id}/redeem", response_model=RedemptionResponse, status_code=status.HTTP_201_CREATED)
async def redeem(reward_id: UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    member = await _get_member(current_user.id, db)
    result = await db.execute(select(Reward).where(Reward.id == reward_id, Reward.family_id == member.family_id, Reward.is_active == True))
    reward = result.scalar_one_or_none()
    if not reward: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if reward.stock == 0: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Out of stock")
    if member.points < reward.points_cost: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not enough stars ({member.points} < {reward.points_cost})")
    existing = await db.execute(select(Redemption).where(Redemption.child_id == current_user.id, Redemption.reward_id == reward_id, Redemption.status == "pending"))
    if existing.scalar_one_or_none(): raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already requested")
    rd = Redemption(child_id=current_user.id, reward_id=reward_id, points_spent=reward.points_cost)
    db.add(rd); await db.flush(); await db.refresh(rd)
    return RedemptionResponse(id=rd.id, child_id=rd.child_id, child_name=await _child_name(current_user.id, db),
            reward_id=rd.reward_id, reward_name=reward.name, points_spent=rd.points_spent,
            status=rd.status, parent_note=rd.parent_note, redeemed_at=rd.redeemed_at, reviewed_at=rd.reviewed_at)


@router.get("/redemptions", response_model=List[RedemptionResponse])
async def list_redemptions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    member = await _get_member(current_user.id, db)
    if member.role == "parent":
        result = await db.execute(select(Redemption, Reward.name).join(Reward, Redemption.reward_id == Reward.id, isouter=True).where(Reward.family_id == member.family_id).order_by(Redemption.redeemed_at.desc()))
    else:
        result = await db.execute(select(Redemption, Reward.name).join(Reward, Redemption.reward_id == Reward.id, isouter=True).where(Redemption.child_id == current_user.id).order_by(Redemption.redeemed_at.desc()))
    out = []
    for rd, rname in result.all():
        out.append(RedemptionResponse(id=rd.id, child_id=rd.child_id, child_name=await _child_name(rd.child_id, db),
            reward_id=rd.reward_id, reward_name=rname, points_spent=rd.points_spent, status=rd.status,
            parent_note=rd.parent_note, redeemed_at=rd.redeemed_at, reviewed_at=rd.reviewed_at))
    return out


@router.post("/redemptions/{redemption_id}/review", response_model=RedemptionResponse)
async def review_redemption(
    redemption_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_req: str = Body(..., embed=True),
    parent_note: Optional[str] = Body(None, embed=True),
):
    member = await _get_member(current_user.id, db)
    if member.role not in ("parent",): raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    result = await db.execute(select(Redemption).where(Redemption.id == redemption_id))
    rd = result.scalar_one_or_none()
    if not rd: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    rd.status = status_req; rd.parent_note = parent_note
    rd.reviewed_by = current_user.id; rd.reviewed_at = datetime.now(timezone.utc)
    if status_req == "approved":
        r2 = await db.execute(select(FamilyMember).where(FamilyMember.family_id == member.family_id, FamilyMember.user_id == rd.child_id))
        cm = r2.scalar_one_or_none()
        if cm: cm.points -= rd.points_spent
    await db.flush(); await db.refresh(rd)
    rname = (await db.execute(select(Reward.name).where(Reward.id == rd.reward_id))).scalar_one_or_none()
    return RedemptionResponse(id=rd.id, child_id=rd.child_id, child_name=await _child_name(rd.child_id, db),
            reward_id=rd.reward_id, reward_name=rname, points_spent=rd.points_spent,
            status=rd.status, parent_note=rd.parent_note, redeemed_at=rd.redeemed_at, reviewed_at=rd.reviewed_at)
