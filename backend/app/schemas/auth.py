from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class UserRegister(BaseModel):
    username: str
    password: str
    name: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str

class ChildLogin(BaseModel):
    invite_code: str
    child_id: UUID


class UserResponse(BaseModel):
    id: UUID
    username: str
    name: str
    role: str
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

