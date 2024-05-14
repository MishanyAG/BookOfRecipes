from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from app.recipes.api_routers import api_get_recipe, api_get_recipes

from app.core.models.recipe import RecipeSchema

view_recipes_router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@view_recipes_router.get("/")
async def view_index(
    request: Request,
    recipes: list[RecipeSchema] = Depends(api_get_recipes),
):
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
    recipe: RecipeSchema = Depends(api_get_recipe),
):
    return templates.TemplateResponse(
        request=request,
        name="recipe.html",
        context={"recipe": recipe},
    )
