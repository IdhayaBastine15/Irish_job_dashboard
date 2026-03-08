from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/irish_jobs"
    sync_database_url: str = "postgresql://postgres:password@localhost:5432/irish_jobs"

    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    adzuna_base_url: str = "https://api.adzuna.com/v1/api/jobs/ie"
    adzuna_results_per_page: int = 50
    adzuna_max_pages: int = 5

    anthropic_api_key: str = ""

    sync_interval_hours: int = 6

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
