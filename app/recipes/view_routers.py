from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_routers import api_logout
from app.auth.helpers import current_user_or_none
from app.core.database import async_db_session
from app.core.models.recipe import RecipeSchema
from app.core.models.user import Role, User
from app.recipes.api_routers import api_get_favorites, api_get_recipe, api_get_recipes

view_recipes_router = APIRouter(tags=["views"])

templates = Jinja2Templates(directory="app/templates")


@view_recipes_router.get("/")
async def view_index(
    request: Request,
    user: User | None = Depends(current_user_or_none),
    recipes: list[RecipeSchema] = Depends(api_get_recipes),
):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "recipes": recipes,
            "user": user.to_schema() if user else None,
        },
    )


@view_recipes_router.get("/recipes/favorites")
async def view_favorites(
    request: Request,
    user: User | None = Depends(current_user_or_none),
    db_session: AsyncSession = Depends(async_db_session),
):
    if user is None:
        return RedirectResponse("/auth/login")

    recipes = await api_get_favorites(user, db_session)
    return templates.TemplateResponse(
        request=request,
        name="favorites.html",
        context={
            "recipes": recipes,
            "user": user.to_schema() if user else None,
        },
    )


@view_recipes_router.get("/recipes/{recipe_id}")
async def view_recipe(
    request: Request,
    user: User | None = Depends(current_user_or_none),
    recipe: RecipeSchema = Depends(api_get_recipe),
):
    return templates.TemplateResponse(
        request=request,
        name="recipe.html",
        context={"recipe": recipe, "user": user.to_schema() if user else None},
    )


@view_recipes_router.get("/admin/recipes")
async def view_create_recipe(
    request: Request,
    user: User | None = Depends(current_user_or_none),
):
    if user is None:
        return RedirectResponse("/auth/login")
    if user.role != Role.ADMIN:
        return RedirectResponse("/auth/login")

    return templates.TemplateResponse(
        request=request,
        name="admin/recipe.html",
        context={"user": user.to_schema()},
    )


@view_recipes_router.get("/admin/recipes/{recipe_id}")
async def view_edit_recipe(
    request: Request,
    user: User | None = Depends(current_user_or_none),
    recipe: RecipeSchema = Depends(api_get_recipe),
):
    if user is None:
        return RedirectResponse("/auth/login")
    if user.role != Role.ADMIN:
        return RedirectResponse("/auth/login")

    return templates.TemplateResponse(
        request=request,
        name="admin/recipe.html",
        context={"recipe": recipe, "user": user.to_schema()},
    )


@view_recipes_router.get("/auth/register")
async def view_register(
    request: Request,
    user: User | None = Depends(current_user_or_none),
):
    if user is not None:
        return RedirectResponse("/")

    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={},
    )


@view_recipes_router.get("/auth/login")
async def view_login(
    request: Request,
    user: User | None = Depends(current_user_or_none),
):
    if user is not None:
        return RedirectResponse("/")

    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={},
    )


@view_recipes_router.get("/auth/logout")
async def view_logout(
    logout=Depends(api_logout),
):
    return RedirectResponse("/")
