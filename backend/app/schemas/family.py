from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class FamilyCreate(BaseModel):
    name: str


class FamilyJoin(BaseModel):
    invite_code: str


class FamilyMemberResponse(BaseModel):
    id: UUID
    name: str
    role: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    points: int

    class Config:
        from_attributes = True


class FamilyResponse(BaseModel):
    id: UUID
    name: str
    invite_code: str
    members: List[FamilyMemberResponse] = []

    class Config:
        from_attributes = True
