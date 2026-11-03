from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SHELF_")

    # The add-on image sets SHELF_DATA_DIR=/data. The default suits local dev.
    data_dir: Path = REPO_DIR / ".data"
    # Built frontend served by FastAPI. Missing in dev, where Vite serves it instead.
    frontend_dist: Path = REPO_DIR / "frontend" / "dist"

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.data_dir / 'shelf-help.db'}"

    @property
    def attachments_dir(self) -> Path:
        return self.data_dir / "attachments"

    def ensure_data_dirs(self) -> None:
        self.attachments_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
