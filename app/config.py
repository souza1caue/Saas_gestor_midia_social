from functools import lru_cache

from pydantic import BaseModel
from dotenv import load_dotenv
import os


load_dotenv()


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "Social Media SaaS")
    secret_key: str = os.getenv("SECRET_KEY", "troque_esta_chave")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
    session_cookie_name: str = "social_media_saas_session"


@lru_cache
def get_settings() -> Settings:
    return Settings()

