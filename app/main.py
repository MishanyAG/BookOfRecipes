from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles

from app.auth.api_routers import api_auth_router
from app.recipes.api_routers import api_recipes_router
from app.recipes.view_routers import view_recipes_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(api_auth_router)
api_v1.include_router(api_recipes_router)

app.include_router(api_v1)
app.include_router(view_recipes_router)
