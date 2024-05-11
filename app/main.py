from fastapi import FastAPI

from app.auth.routers import auth_router
from app.recipes.routers import recipes_router

app = FastAPI()


app.include_router(auth_router)
app.include_router(recipes_router)
