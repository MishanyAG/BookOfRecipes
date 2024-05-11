from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseORM, BaseSchema


class CreateRecipeSchema(BaseSchema):
    name: str
    description: str
    action_to_cook: str
    image_link: str
    ingredients: dict[str, str]
    tags: list[str]


class RecipeSchema(CreateRecipeSchema):
    recipe_id: UUID


class Recipe(BaseORM):
    __tablename__ = "recipes"
    _schema = RecipeSchema

    recipe_id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column()
    action_to_cook: Mapped[str] = mapped_column()

    image_id: Mapped[UUID] = mapped_column(ForeignKey("images.image_id"), unique=True)
    image: Mapped["Image"] = relationship("Image", back_populates="recipe")

    ingredients: Mapped[dict[str, str]] = mapped_column(JSONB, default=dict)
    tags: Mapped[list] = mapped_column(JSONB, default=list)


class Image(BaseORM):
    __tablename__ = "images"

    image_id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    image_link: Mapped[str] = mapped_column(unique=True)

    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="image")


class UserFavorite(BaseORM):
    __tablename__ = "user_favorites"

    recipe_id: Mapped[UUID] = mapped_column(
        ForeignKey("recipes.recipe_id"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
