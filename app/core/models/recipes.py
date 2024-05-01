from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseORM


class Tag(BaseORM):
    __tablename__ = "tags"

    tag_id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    name: Mapped[str] = mapped_column()

    recipes = relationship("TagRecipe", back_populates="tag")


class TagRecipe(BaseORM):
    __tablename__ = "tag_recipe"

    recipe_id: Mapped[UUID] = mapped_column(
        ForeignKey("recipes.recipe_id"), primary_key=True
    )
    tag_id: Mapped[UUID] = mapped_column(ForeignKey("tags.tag_id"), primary_key=True)

    recipe = relationship("Recipe", back_populates="tags")
    tag = relationship("Tag", back_populates="recipes")


class Recipe(BaseORM):
    __tablename__ = "recipes"

    recipe_id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str] = mapped_column()
    action_to_cook: Mapped[str] = mapped_column()
    image_link: Mapped[str] = mapped_column()

    tags = relationship("TagRecipe", back_populates="recipe")
    ingredients = relationship("IngredientRecipe", back_populates="recipe")


class Ingredient(BaseORM):
    __tablename__ = "ingredients"

    ingredient_id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    name: Mapped[str] = mapped_column()

    recipes = relationship("IngredientRecipe", back_populates="ingredients")


class IngredientRecipe(BaseORM):
    __tablename__ = "ingredient_recipe"

    recipe_id: Mapped[UUID] = mapped_column(
        ForeignKey("recipes.recipe_id"), primary_key=True
    )
    ingredient_id: Mapped[UUID] = mapped_column(
        ForeignKey("ingredients.ingredient_id"), primary_key=True
    )

    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipes")


class UserFavorite(BaseORM):
    __tablename__ = "user_favorites"

    recipe_id: Mapped[UUID] = mapped_column(
        ForeignKey("recipes.recipe_id"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
