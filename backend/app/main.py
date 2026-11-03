from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute

from app.core import health
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.frontend import mount_frontend
from app.modules.items import router as items
from app.modules.locations import router as locations
from app.modules.projects import router as projects
from app.modules.shopping import router as shopping
from app.modules.tags import router as tags


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
    api.include_router(locations.router)
    api.include_router(items.router)
    api.include_router(projects.router)
    api.include_router(tags.router)
    api.include_router(shopping.router)

    app.include_router(api)
    register_error_handlers(app)
    # Last, so its catch-all route doesn't shadow the API.
    mount_frontend(app, settings.frontend_dist)
    return app
