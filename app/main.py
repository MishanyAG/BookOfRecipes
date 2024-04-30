from fastapi import FastAPI
from app.auth.api import auth_router

app = FastAPI()


app.include_router(auth_router)
