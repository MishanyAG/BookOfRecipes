import logging
from uuid import UUID, uuid4

from fastapi import APIRouter, Cookie, Depends, Form, HTTPException
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.helpers import (
    SessionService,
    current_user,
    hash_raw_password,
    verify_raw_password,
)
from app.core.config import USER_SESSION_COOKIE_NAME
from app.core.database import async_db_session
from app.core.models.user import User, UserSchema

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler("auth.log")
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
logging.getLogger().setLevel(logging.WARNING)

api_auth_router = APIRouter(prefix="/auth", tags=["auth"])


@api_auth_router.post("/register", response_model=UserSchema)
async def api_register(
    session_service: SessionService = Depends(SessionService),
    email: EmailStr = Form(),
    nickname: str = Form(),
    password: str = Form(min_length=8, max_length=50),
    db_session: AsyncSession = Depends(async_db_session),
):
    user = await db_session.scalar(select(User.user_id).where(User.email == email))

    if user is not None:
        logger.warning(f"Пользователь {email} уже существует")
        raise HTTPException(400, "User already exists")

    user = User(
        user_id=uuid4(),
        email=email,
        nickname=nickname,
        hashed_password=hash_raw_password(password),
    )

    db_session.add(user)
    await db_session.commit()

    await session_service.save_session(user.user_id)

    logger.info(f"Пользователь {user.email} прошёл регистрацию")
    return user.to_schema()


@api_auth_router.get("/info", response_model=UserSchema)
async def api_user_info(
    user: User = Depends(current_user),
):
    return user.to_schema()


@api_auth_router.post("/login", response_model=UserSchema)
async def api_login(
    session_service: SessionService = Depends(SessionService),
    email: EmailStr = Form(),
    password: str = Form(min_length=8, max_length=50),
    db_session: AsyncSession = Depends(async_db_session),
):
    user = await db_session.scalar(select(User).where(User.email == email))

    if user is None or not verify_raw_password(password, user.hashed_password):
        logger.warning(f"Пользователь {email} не прошёл авторизацию")
        raise HTTPException(401)

    await session_service.refresh_session(user.user_id)

    logger.info(f"Пользователь {user.email} прошёл авторизацию")
    return user.to_schema()


@api_auth_router.post("/logout")
async def api_logout(
    session_service: SessionService = Depends(SessionService),
    user_session_cookie: str | None = Cookie(None, alias=USER_SESSION_COOKIE_NAME),
    db_session: AsyncSession = Depends(async_db_session),
):
    if user_session_cookie is None:
        raise HTTPException(401)

    user_id, _ = user_session_cookie.split(".")
    await session_service.delete_session(UUID(user_id))

    email = await db_session.scalar(
        select(User.email).where(User.user_id == UUID(user_id))
    )
    logger.info(f"Пользователь {email} вышел из системы")
