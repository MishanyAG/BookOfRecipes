"""recipes

Revision ID: 4a1db16d688a
Revises: def51074c45e
Create Date: 2024-05-01 15:12:50.707207

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4a1db16d688a"
down_revision: Union[str, None] = "def51074c45e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "recipes",
        sa.Column("recipe_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("action_to_cook", sa.String(), nullable=False),
        sa.Column("image_link", sa.String(), nullable=False),
        sa.Column('ingredients', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("recipe_id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "user_favorites",
        sa.Column("recipe_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.recipe_id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
        ),
        sa.PrimaryKeyConstraint("recipe_id", "user_id"),
    )


def downgrade() -> None:
    op.drop_table("user_favorites")
    op.drop_table("recipes")
