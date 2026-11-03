from datetime import UTC, datetime

from fastapi import APIRouter, FastAPI

from app.core.config import settings
from app.core.frontend import mount_frontend


def create_app() -> FastAPI:
    app = FastAPI(
        title="Shelf-help",
        docs_url="/api/docs",
        redoc_url=None,
        openapi_url="/api/openapi.json",
    )

    api = APIRouter(prefix="/api")

    @api.get("/health")
    def get_health() -> dict[str, str]:
        return {"status": "ok", "time": datetime.now(UTC).isoformat()}

    app.include_router(api)
    # Last, so its catch-all route doesn't shadow the API.
    mount_frontend(app, settings.frontend_dist)
    return app
