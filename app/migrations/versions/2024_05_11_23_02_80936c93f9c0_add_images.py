"""add images

Revision ID: 80936c93f9c0
Revises: 4a1db16d688a
Create Date: 2024-05-11 23:02:57.024450

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "80936c93f9c0"
down_revision: Union[str, None] = "4a1db16d688a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "images",
        sa.Column("image_id", sa.Uuid(), nullable=False),
        sa.Column("image_link", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("image_id"),
    )
    op.add_column("recipes", sa.Column("image_id", sa.Uuid(), nullable=False))
    op.create_foreign_key(
        "recipes_image_id_fkey", "recipes", "images", ["image_id"], ["image_id"]
    )
    op.drop_column("recipes", "image_link")


def downgrade() -> None:
    op.add_column(
        "recipes",
        sa.Column("image_link", sa.VARCHAR(), autoincrement=False, nullable=False),
    )
    op.drop_constraint("recipes_image_id_fkey", "recipes", type_="foreignkey")
    op.drop_column("recipes", "image_id")
    op.drop_table("images")
