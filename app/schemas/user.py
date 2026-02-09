from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password_hash: str
    name: str | None = None


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str | None
    created_at: datetime

    class Config:
        from_attributes = True
