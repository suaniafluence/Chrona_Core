from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.db import get_session
from src.models.user import User
from src.routers.auth import require_roles
from src.schemas import UserRead


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ping")
async def ping_admin(current: Annotated[User, Depends(require_roles("admin"))]):
    return {"pong": True, "role": current.role}


class SetRoleRequest(BaseModel):
    role: str


@router.patch("/users/{user_id}/role", response_model=UserRead)
async def set_user_role(
    user_id: int,
    payload: SetRoleRequest,
    _current: Annotated[User, Depends(require_roles("admin"))],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    allowed = {"admin", "user"}
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
