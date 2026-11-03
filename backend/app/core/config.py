from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SHELF_")

    # Built frontend served by FastAPI. Missing in dev, where Vite serves it instead.
    frontend_dist: Path = BACKEND_DIR.parent / "frontend" / "dist"


settings = Settings()
