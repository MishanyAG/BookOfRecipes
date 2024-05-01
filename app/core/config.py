import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST: str = os.environ.get("POSTGRES_HOST")  # type: ignore
DB_PORT: str = os.environ.get("POSTGRES_PORT")  # type: ignore
DB_USER: str = os.environ.get("POSTGRES_USER")  # type: ignore
DB_PASS: str = os.environ.get("POSTGRES_PASSWORD")  # type: ignore
DB_NAME: str = os.environ.get("POSTGRES_DB")  # type: ignore

ASYNC_DATABASE_URL: str = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

USER_SESSION_COOKIE_NAME: str = os.environ.get("USER_SESSION_COOKIE_NAME")  # type: ignore
USER_SESSION_EXP: int = int(os.environ.get("USER_SESSION_EXP"))  # type: ignore
USER_SESSION_REFRESH: int = int(os.environ.get("USER_SESSION_REFRESH"))  # type: ignore

SALT_SIZE: int = int(os.environ.get("SALT_SIZE"))  # type: ignore
