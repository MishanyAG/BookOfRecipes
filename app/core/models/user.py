from datetime import date, datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ENUM as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseORM, BaseSchema


class Role(Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class UserSchema(BaseSchema):
    user_id: UUID
    nickname: str
    email: EmailStr
    created_at: date
    role: Role


class User(BaseORM):
    __tablename__ = "users"
    _schema = UserSchema

    user_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nickname: Mapped[str] = mapped_column(String(length=50), nullable=False)
    email: Mapped[str] = mapped_column(String(length=50), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[date] = mapped_column(nullable=False, default=date.today)
    role: Mapped[Role] = mapped_column(
        SQLEnum(Role, name="enum_user_roles"), nullable=False, default=Role.USER
    )

    session: Mapped["UserSession"] = relationship("UserSession", back_populates="user")


class UserSession(BaseORM):
    __tablename__ = "users_session"

    session_id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.user_id"), unique=True, nullable=False
    )
    expiration_at: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )

    user: Mapped["User"] = relationship("User", back_populates="session")
