from typing import Annotated, Callable

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.db import get_session
from src.models.user import User
from src.schemas import Token, UserCreate, UserRead
from src.security import (
    create_access_token,
    decode_token,
    get_password_hash,
    verify_password,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
async def register_user(
    payload: UserCreate, session: Annotated[AsyncSession, Depends(get_session)]
):
    user = User(
        email=payload.email, hashed_password=get_password_hash(payload.password)
    )
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="email_already_registered")
    return UserRead.model_validate(user)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials"
        )
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return Token(access_token=token)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token"
        )
    user_id = int(payload["sub"])
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="user_not_found"
        )
    return user


def require_roles(*roles: str) -> Callable[[User], User]:
    async def _dep(current: Annotated[User, Depends(get_current_user)]) -> User:
        if roles and current.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="forbidden"
            )
        return current

    return _dep


@router.get("/me", response_model=UserRead)
async def read_me(current: Annotated[User, Depends(get_current_user)]):
    return UserRead.model_validate(current)
