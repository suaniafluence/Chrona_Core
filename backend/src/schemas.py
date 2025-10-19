from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

try:
    # Pydantic v2
    from pydantic import ConfigDict  # type: ignore
except Exception:  # pragma: no cover
    ConfigDict = dict  # fallback for type checking


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # allow ORM objects
    id: int
    email: EmailStr
    role: str
    created_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str
