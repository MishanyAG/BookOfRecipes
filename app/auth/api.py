from uuid import uuid4

from fastapi import APIRouter, Depends, Form, HTTPException, Response, Cookie
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_db_session
from app.core.models.user import User, UserSchema, UserSession
from app.auth.helpers import hash_raw_password, verify_raw_password, SessionService, current_user
from app.core.config import USER_SESSION_COOKIE_NAME

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserSchema)
async def api_register(
    session_service: SessionService = Depends(SessionService),
    email: EmailStr = Form(),
    nickname: str = Form(),
    password: str = Form(min_length=8, max_length=50),
    db_session: AsyncSession = Depends(async_db_session),
):
    user = await db_session.scalar(select(User.user_id).where(User.email == email))

    if user is not None:
        raise HTTPException(400)

    user = User(
        user_id=uuid4(),
        email=email,
        nickname=nickname,
        hashed_password=hash_raw_password(password),
    )

    db_session.add(user)
    await db_session.commit()

    await session_service.save_session(user.user_id)

    return user.to_schema()


@auth_router.get("/info", response_model=UserSchema)
async def api_user_info(
    user: User = Depends(current_user),
):
    return user.to_schema()


@auth_router.post("/login", response_model=UserSchema)
async def api_login(
    session_service: SessionService = Depends(SessionService),
    email: EmailStr = Form(),
    password: str = Form(min_length=8, max_length=50),
    db_session: AsyncSession = Depends(async_db_session),
):
    user = await db_session.scalar(select(User).where(User.email == email))
    if user is None or not verify_raw_password(
        password, user.hashed_password
    ):
        raise HTTPException(401)

    await session_service.refresh_session(user.user_id)

    return user.to_schema()


@auth_router.post("/logout")
async def api_logout(
    session_service: SessionService = Depends(SessionService),
    user_session_cookie: str = Cookie(None, alias=USER_SESSION_COOKIE_NAME),
    db_session: AsyncSession = Depends(async_db_session),
):
    if user_session_cookie is not None:
        user = await current_user(session_service, user_session_cookie, db_session)
        await session_service.delete_session(user.user_id)
