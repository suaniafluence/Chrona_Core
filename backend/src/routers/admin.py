from typing import Annotated

from fastapi import APIRouter, Depends

from src.models.user import User
from src.routers.auth import require_roles


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ping")
async def ping_admin(current: Annotated[User, Depends(require_roles("admin"))]):
    return {"pong": True, "role": current.role}

