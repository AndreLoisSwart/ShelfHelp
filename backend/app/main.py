from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute

from app.core import health
from app.core.config import settings
from app.core.frontend import mount_frontend


def operation_id(route: APIRoute) -> str:
    # The function name, so generated hooks read like useGetHealth.
    return route.name


def create_app() -> FastAPI:
    app = FastAPI(
        title="Shelf-help",
        docs_url="/api/docs",
        redoc_url=None,
        openapi_url="/api/openapi.json",
        generate_unique_id_function=operation_id,
    )

    api = APIRouter(prefix="/api")
    api.include_router(health.router)

    app.include_router(api)
    # Last, so its catch-all route doesn't shadow the API.
    mount_frontend(app, settings.frontend_dist)
    return app
