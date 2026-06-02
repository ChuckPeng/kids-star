import secrets, uuid
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models.models import User, Family, FamilyMember
from app.schemas.family import FamilyCreate, FamilyJoin, FamilyMemberCreate, FamilyResponse, FamilyMemberResponse

router = APIRouter(prefix="/families", tags=["families"])


def _generate_invite_code() -> str:
    return secrets.token_hex(4).upper()


async def _get_family_response(family: Family, db: AsyncSession) -> FamilyResponse:
    result = await db.execute(
        select(FamilyMember).where(FamilyMember.family_id == family.id).options(selectinload(FamilyMember.user))
    )
    members_raw = result.scalars().all()
    members = [
        FamilyMemberResponse(
            id=m.user.id,
            name=m.user.name,
            role=m.role,
            nickname=m.nickname,
            avatar_url=m.avatar_url,
            points=m.points,
        )
        for m in members_raw
    ]
    return FamilyResponse(
        id=family.id,
        name=family.name,
        invite_code=family.invite_code,
        members=members,
    )


@router.post("", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
async def create_family(
    data: FamilyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    family = Family(
        name=data.name,
        invite_code=_generate_invite_code(),
        created_by=current_user.id,
    )
    db.add(family)
    await db.flush()

    member = FamilyMember(
        user_id=current_user.id,
        family_id=family.id,
        role="parent",
    )
    db.add(member)
    await db.flush()
    await db.refresh(family)

    return await _get_family_response(family, db)


@router.post("/join", response_model=FamilyResponse)
async def join_family(
    data: FamilyJoin,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Family).where(Family.invite_code == data.invite_code.upper()))
    family = result.scalar_one_or_none()
    if not family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid invite code")

    # Check if already a member
    existing = await db.execute(
        select(FamilyMember).where(
            FamilyMember.user_id == current_user.id,
            FamilyMember.family_id == family.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already a member of this family")

    member = FamilyMember(
        user_id=current_user.id,
        family_id=family.id,
        role=current_user.role,  # parent or child
        nickname=current_user.name,
    )
    db.add(member)
    await db.flush()

    return await _get_family_response(family, db)




@router.get("/lookup/{invite_code}")
async def lookup_family_children(
    invite_code: str,
    db: AsyncSession = Depends(get_db),
):
    """Lookup children in a family by invite code (for child login)."""
    result = await db.execute(
        select(Family).where(Family.invite_code == invite_code.upper())
    )
    family = result.scalar_one_or_none()
    if not family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid invite code")

    result = await db.execute(
        select(FamilyMember, User)
        .join(User, FamilyMember.user_id == User.id)
        .where(
            FamilyMember.family_id == family.id,
            FamilyMember.role == "child",
            User.is_active == True,
        )
    )
    rows = result.all()
    return [
        {"id": str(user.id), "name": user.name, "nickname": member.nickname}
        for member, user in rows
    ]

@router.post("/children", response_model=FamilyMemberResponse, status_code=status.HTTP_201_CREATED)
async def create_child(
    data: FamilyMemberCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a child account in the family (parent only)."""
    # Verify parent is in a family
    result = await db.execute(
        select(FamilyMember).where(FamilyMember.user_id == current_user.id)
    )
    parent_member = result.scalar_one_or_none()
    if not parent_member or parent_member.role != "parent":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Parent access required")

    # Create child user (no password - simplified login)
    child_user = User(
        username=f"child_{uuid.uuid4().hex[:8]}",
        password_hash="",
        name=data.nickname or data.name,
        role="child",
    )
    db.add(child_user)
    await db.flush()

    # Add to family
    member = FamilyMember(
        user_id=child_user.id,
        family_id=parent_member.family_id,
        role="child",
        nickname=data.nickname or data.name,
    )
    db.add(member)
    await db.flush()
    await db.refresh(member)

    return FamilyMemberResponse(
        id=child_user.id,
        name=child_user.name,
        role=member.role,
        nickname=member.nickname,
        avatar_url=member.avatar_url,
        points=member.points,
    )

@router.get("/me", response_model=Optional[FamilyResponse])
async def get_my_family(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FamilyMember).where(FamilyMember.user_id == current_user.id)
    )
    member = result.scalar_one_or_none()
    if not member:
        return None

    result = await db.execute(select(Family).where(Family.id == member.family_id))
    family = result.scalar_one()

    return await _get_family_response(family, db)




