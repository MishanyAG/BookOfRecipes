"""recipes

Revision ID: 4a1db16d688a
Revises: def51074c45e
Create Date: 2024-05-01 15:12:50.707207

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4a1db16d688a"
down_revision: Union[str, None] = "def51074c45e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "ingredients",
        sa.Column("ingredient_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("ingredient_id"),
    )
    op.create_table(
        "recipes",
        sa.Column("recipe_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("action_to_cook", sa.String(), nullable=False),
        sa.Column("image_link", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("recipe_id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "tags",
        sa.Column("tag_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("tag_id"),
    )
    op.create_table(
        "ingredient_recipe",
        sa.Column("recipe_id", sa.Uuid(), nullable=False),
        sa.Column("ingredient_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["ingredient_id"],
            ["ingredients.ingredient_id"],
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.recipe_id"],
        ),
        sa.PrimaryKeyConstraint("recipe_id", "ingredient_id"),
    )
    op.create_table(
        "tag_recipe",
        sa.Column("recipe_id", sa.Uuid(), nullable=False),
        sa.Column("tag_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.recipe_id"],
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tags.tag_id"],
        ),
        sa.PrimaryKeyConstraint("recipe_id", "tag_id"),
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
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_favorites")
    op.drop_table("tag_recipe")
    op.drop_table("ingredient_recipe")
    op.drop_table("tags")
    op.drop_table("recipes")
    op.drop_table("ingredients")
    # ### end Alembic commands ###
