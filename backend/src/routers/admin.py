from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.db import get_session
from src.models.user import User
from src.routers.auth import require_roles
from src.schemas import AdminUserCreate, UserRead
from src.security import get_password_hash


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ping")
async def ping_admin(_current: Annotated[User, Depends(require_roles("admin"))]):
    return {"message": "Admin access OK"}


class SetRoleRequest(BaseModel):
    role: str


@router.api_route("/users/{user_id}/role", methods=["PATCH", "POST"], response_model=UserRead)
async def set_user_role(
    user_id: int,
    payload: SetRoleRequest,
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    allowed = {"admin", "user", "manager"}
    role = payload.role.strip().lower()
    if role not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_role")

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user_not_found")

    user.role = role
    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)


@router.get("/users", response_model=list[UserRead])
async def list_users(
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
    offset: int = 0,
    limit: int = 50,
):
    if limit > 100:
        limit = 100
    result = await session.execute(select(User).offset(offset).limit(limit))
    users = result.scalars().all()
    return [UserRead.model_validate(u) for u in users]


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user_not_found")
    return UserRead.model_validate(user)


@router.post("/users", response_model=UserRead, status_code=201)
async def create_user_with_role(
    payload: AdminUserCreate,
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    allowed = {"admin", "user", "manager"}
    role = payload.role.strip().lower()
    if role not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_role")
    user = User(email=payload.email, hashed_password=get_password_hash(payload.password), role=role)
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
    except Exception:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email_already_registered")
    return UserRead.model_validate(user)
