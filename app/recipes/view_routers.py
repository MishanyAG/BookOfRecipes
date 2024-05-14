from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.templating import Jinja2Templates

from app.core.database import AsyncSession, async_db_session
from app.recipes.api_routers import api_get_recipe, api_get_recipes

view_recipes_router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@view_recipes_router.get("/")
async def view_index(
    request: Request,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    name: str | None = Query(None),
    tags: list[str] | None = Query(None),
    ingredients: list[str] | None = Query(None),
    db_session: AsyncSession = Depends(async_db_session),
):
    recipes = await api_get_recipes(
        offset=offset,
        limit=limit,
        name=name,
        tags=tags,
        ingredients=ingredients,
        db_session=db_session,
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "recipes": recipes,
        },
    )


@view_recipes_router.get("/recipes/{recipe_id}")
async def view_recipe(
    request: Request,
    recipe_id: UUID,
    db_session: AsyncSession = Depends(async_db_session),
):
    recipe = await api_get_recipe(recipe_id=recipe_id, db_session=db_session)

    return templates.TemplateResponse(
        request=request,
        name="recipe.html",
        context={"recipe": recipe},
    )
