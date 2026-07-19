from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Study Planner MVP1"
    DATABASE_URL: str = "sqlite+aiosqlite:///./study_planner.db"
    JWT_SECRET_KEY: str = "change-this-to-a-secure-random-string-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
