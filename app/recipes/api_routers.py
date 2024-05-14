from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.auth.helpers import (
    current_admin,
    current_user,
)
from app.core.database import async_db_session
from app.core.models.recipe import (
    CreateRecipeSchema,
    Image,
    Recipe,
    RecipeSchema,
    UserFavorite,
)
from app.core.models.user import User

api_recipes_router = APIRouter(prefix="/recipes", tags=["recipes"])


@api_recipes_router.post("/", response_model=RecipeSchema)
async def api_create_recipe(
    recipe_schema: CreateRecipeSchema,
    admin: User = Depends(current_admin),
    db_session: AsyncSession = Depends(async_db_session),
):
    recipe = await db_session.scalar(
        select(Recipe.recipe_id).where(Recipe.name == recipe_schema.name)
    )
    if recipe is not None:
        raise HTTPException(400, "Recipe already exists")

    image_id = await db_session.scalar(
        select(Image.image_id).where(Image.image_link == recipe_schema.image_link)
    )
    if image_id is None:
        image_id = uuid4()
        image = Image(image_id=image_id, image_link=recipe_schema.image_link)
        db_session.add(image)

    recipe = Recipe(
        image_id=image_id,
        name=recipe_schema.name,
        description=recipe_schema.description,
        action_to_cook=recipe_schema.action_to_cook,
        ingredients=recipe_schema.ingredients,
        tags=recipe_schema.tags,
    )

    db_session.add(recipe)
    await db_session.commit()

    return recipe.to_schema(image_link=recipe_schema.image_link)


@api_recipes_router.get("/", response_model=list[RecipeSchema])
async def api_get_recipes(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    name: str | None = Query(None),
    tags: list[str] | None = Query(None),
    ingredients: list[str] | None = Query(None),
    db_session: AsyncSession = Depends(async_db_session),
):
    query = (
        select(Recipe)
        .offset(offset)
        .limit(limit)
        .options(joinedload(Recipe.image).load_only(Image.image_link))
    )

    if name:
        query = query.where(Recipe.name.ilike(f"%{name}%"))
    if tags:
        query = query.where(Recipe.tags.contains(tags))
    if ingredients:
        query = query.where(func.jsonb_exists_any(Recipe.ingredients, ingredients))

    recipes = await db_session.scalars(query)
    return [recipe.to_schema(image_link=recipe.image.image_link) for recipe in recipes]


@api_recipes_router.get("/favorites", response_model=list[RecipeSchema])
async def api_get_favorites(
    user: User = Depends(current_user),
    db_session: AsyncSession = Depends(async_db_session),
):
    recipes = await db_session.scalars(
        select(Recipe)
        .join(UserFavorite, UserFavorite.recipe_id == Recipe.recipe_id)
        .where(UserFavorite.user_id == user.user_id)
        .options(joinedload(Recipe.image).load_only(Image.image_link))
    )
    return [recipe.to_schema(image_link=recipe.image.image_link) for recipe in recipes]


@api_recipes_router.get("/{recipe_id}", response_model=RecipeSchema)
async def api_get_recipe(
    recipe_id: UUID,
    db_session: AsyncSession = Depends(async_db_session),
):
    recipe = await db_session.get(
        Recipe,
        recipe_id,
        options=[joinedload(Recipe.image).load_only(Image.image_link)],
    )
    if recipe is None:
        raise HTTPException(404, "Recipe not found")

    return recipe.to_schema(image_link=recipe.image.image_link)


@api_recipes_router.delete("/{recipe_id}")
async def api_delete_recipe(
    recipe_id: UUID,
    admin: User = Depends(current_admin),
    db_session: AsyncSession = Depends(async_db_session),
):
    recipe = await db_session.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(404, "Recipe not found")
    await db_session.delete(recipe)
    await db_session.commit()


@api_recipes_router.post("/{recipe_id}/favorite")
async def api_favorite_recipe(
    recipe_id: UUID,
    user: User = Depends(current_user),
    db_session: AsyncSession = Depends(async_db_session),
):
    user_favorite = await db_session.get(UserFavorite, (recipe_id, user.user_id))
    if user_favorite is not None:
        raise HTTPException(400, "Recipe already favorited")

    user_favorite = UserFavorite(recipe_id=recipe_id, user_id=user.user_id)
    db_session.add(user_favorite)
    await db_session.commit()


@api_recipes_router.delete("/{recipe_id}/favorite")
async def api_unfavorite_recipe(
    recipe_id: UUID,
    user: User = Depends(current_user),
    db_session: AsyncSession = Depends(async_db_session),
):
    user_favorite = await db_session.get(UserFavorite, (recipe_id, user.user_id))
    if user_favorite is None:
        raise HTTPException(400, "Recipe not favorited")

    await db_session.delete(user_favorite)
    await db_session.commit()
