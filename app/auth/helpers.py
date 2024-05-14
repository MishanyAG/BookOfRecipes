import base64
import hashlib
import os
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from fastapi import Cookie, Depends, HTTPException, Response
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.config import (
    SALT_SIZE,
    USER_SESSION_COOKIE_NAME,
    USER_SESSION_EXP,
    USER_SESSION_REFRESH,
)
from app.core.database import async_db_session
from app.core.models.user import Role, User, UserSession


def hash_raw_password(raw_password: str):
    salt = os.urandom(SALT_SIZE)
    key = hashlib.pbkdf2_hmac("sha256", raw_password.encode(), salt, 100000)
    return base64.b64encode(salt + key).decode()


def verify_raw_password(raw_password: str, hashed_password: str):
    decoded = base64.b64decode(hashed_password.encode())
    salt = decoded[:SALT_SIZE]
    key = decoded[SALT_SIZE:]
    new_key = hashlib.pbkdf2_hmac("sha256", raw_password.encode(), salt, 100000)
    return key == new_key


class SessionService:
    def __init__(
        self, response: Response, db_session: AsyncSession = Depends(async_db_session)
    ):
        self._response = response
        self._db_session = db_session

    @classmethod
    def is_need_refresh(cls, user_session: UserSession):
        return (
            user_session.created_at + timedelta(seconds=USER_SESSION_REFRESH)
            <= datetime.utcnow()
        )

    @classmethod
    def create_session(cls, user_id: UUID):
        _now = datetime.utcnow()
        return UserSession(
            session_id=uuid4(),
            user_id=user_id,
            created_at=_now,
            expiration_at=_now + timedelta(seconds=USER_SESSION_EXP),
        )

    async def delete_session(self, user_id: UUID | None):
        self._response.delete_cookie(USER_SESSION_COOKIE_NAME)
        if user_id:
            await self._db_session.execute(
                delete(UserSession).where(UserSession.user_id == user_id)
            )
            await self._db_session.commit()

    async def save_session(self, user_id: UUID):
        user_session = self.create_session(user_id)
        self._db_session.add(user_session)
        await self._db_session.commit()
        self._response.set_cookie(
            USER_SESSION_COOKIE_NAME,
            f"{user_id}.{user_session.session_id}",
            max_age=USER_SESSION_EXP,
            path="/",
            httponly=True,
            secure=True,
            samesite="strict",
        )

    async def refresh_session(self, user_id: UUID):
        await self.delete_session(user_id)
        await self.save_session(user_id)


async def current_admin(
    session_service: SessionService = Depends(SessionService),
    user_session_cookie: str = Cookie(None, alias=USER_SESSION_COOKIE_NAME),
    db_session: AsyncSession = Depends(async_db_session),
):
    user = await current_user(session_service, user_session_cookie, db_session)
    if user.role != Role.ADMIN:
        raise HTTPException(403)
    return user


async def current_user(
    session_service: SessionService = Depends(SessionService),
    user_session_cookie: str = Cookie(None, alias=USER_SESSION_COOKIE_NAME),
    db_session: AsyncSession = Depends(async_db_session),
) -> User:
    if user_session_cookie is None:
        raise HTTPException(401)

    user_id, user_session_id = user_session_cookie.split(".")
    user_session = await db_session.scalar(
        select(UserSession)
        .where(UserSession.session_id == UUID(user_session_id))
        .where(UserSession.user_id == UUID(user_id))
        .options(joinedload(UserSession.user))
    )

    if user_session is None:
        raise HTTPException(401)

    user = user_session.user

    if user_session.expiration_at <= datetime.utcnow():
        await session_service.delete_session(user.user_id)
        raise HTTPException(401)

    if SessionService.is_need_refresh(user_session):
        await session_service.refresh_session(user.user_id)

    return user
