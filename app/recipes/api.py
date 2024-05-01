from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Form, HTTPException, Cookie
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_db_session
from app.core.models.user import User, UserSchema
from app.auth.helpers import (
    hash_raw_password,
    verify_raw_password,
    SessionService,
    current_user,
)
from app.core.config import USER_SESSION_COOKIE_NAME

recipes_router = APIRouter(prefix="/auth", tags=["auth"])


