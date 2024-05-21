from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.auth.helpers import (
    current_admin,
    current_user,
    current_user_or_none,
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


@api_recipes_router.put("/{recipe_id}", response_model=RecipeSchema)
async def api_update_recipe(
    recipe_id: UUID,
    recipe_schema: CreateRecipeSchema,
    admin: User = Depends(current_admin),
    db_session: AsyncSession = Depends(async_db_session),
):
    recipe = await db_session.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(404, "Recipe not found")

    image_id = await db_session.scalar(
        select(Image.image_id).where(Image.image_link == recipe_schema.image_link)
    )
    if image_id is None:
        image_id = uuid4()
        image = Image(image_id=image_id, image_link=recipe_schema.image_link)
        db_session.add(image)

    recipe.image_id = image_id
    recipe.name = recipe_schema.name
    recipe.description = recipe_schema.description
    recipe.action_to_cook = recipe_schema.action_to_cook
    recipe.ingredients = recipe_schema.ingredients
    recipe.tags = recipe_schema.tags

    await db_session.commit()

    return recipe.to_schema(image_link=recipe_schema.image_link)


@api_recipes_router.get("/", response_model=list[RecipeSchema])
async def api_get_recipes(
    name: str | None = Query(None),
    tags: list[str] | None = Query(None),
    ingredients: list[str] | None = Query(None),
    user: User | None = Depends(current_user_or_none),
    db_session: AsyncSession = Depends(async_db_session),
):
    query = select(Recipe).options(joinedload(Recipe.image).load_only(Image.image_link))

    if user is not None:
        query = query.outerjoin(
            UserFavorite,
            and_(
                UserFavorite.recipe_id == Recipe.recipe_id,
                UserFavorite.user_id == user.user_id,
            ),
        )
        query = query.add_columns(UserFavorite.recipe_id)

    if name:
        query = query.where(Recipe.name.ilike(f"%{name}%"))
    if tags:
        query = query.where(Recipe.tags.contains(tags))
    if ingredients:
        query = query.where(func.jsonb_exists_all(Recipe.ingredients, ingredients))

    recipes = await db_session.execute(query)
    return [
        recipe.Recipe.to_schema(
            image_link=recipe.Recipe.image.image_link,
            is_favorite=bool(recipe.recipe_id) if user else False,
        )
        for recipe in recipes
    ]


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
    return [
        recipe.to_schema(image_link=recipe.image.image_link, is_favorite=True)
        for recipe in recipes
    ]


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


@api_recipes_router.post("/{recipe_id}/favorites")
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


@api_recipes_router.delete("/{recipe_id}/favorites")
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
