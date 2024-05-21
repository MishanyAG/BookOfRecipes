"""create admin user

Revision ID: 4abbaeeb124e
Revises: 80936c93f9c0
Create Date: 2024-05-21 22:42:20.186347

"""

from datetime import date
from typing import Sequence, Union
from uuid import uuid4

from alembic import op

from app.auth.helpers import hash_raw_password
from app.core.config import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_USERNAME
from app.core.models.user import User

# revision identifiers, used by Alembic.
revision: str = "4abbaeeb124e"
down_revision: Union[str, None] = "80936c93f9c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

assert ADMIN_USERNAME is not None, "ADMIN_USERNAME is not set"
assert ADMIN_PASSWORD is not None, "ADMIN_PASSWORD is not set"
assert ADMIN_EMAIL is not None, "ADMIN_EMAIL is not set"

user = {
    "user_id": uuid4(),
    "nickname": ADMIN_USERNAME,
    "email": ADMIN_EMAIL,
    "hashed_password": hash_raw_password(ADMIN_PASSWORD),
    "role": "ADMIN",
    "created_at": date.today(),
}


def upgrade() -> None:
    op.bulk_insert(User.__table__, [user])  # type: ignore


def downgrade() -> None:
    op.execute(f"DELETE FROM users WHERE email = '{ADMIN_EMAIL}'")
