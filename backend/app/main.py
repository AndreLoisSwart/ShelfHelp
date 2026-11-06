from collections.abc import Iterator
from contextlib import contextmanager

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from mcp.server.transport_security import TransportSecuritySettings
from sqlalchemy.orm import Session

from app.core import health
from app.core.access import AccessMiddleware
from app.core.config import settings
from app.core.db import get_session
from app.core.errors import register_error_handlers
from app.core.frontend import mount_frontend
from app.modules.attachments import router as attachments
from app.modules.dashboard import router as dashboard
from app.modules.inbox import router as inbox
from app.modules.items import router as items
from app.modules.links import router as links
from app.modules.locations import router as locations
from app.modules.mcp import router as mcp
from app.modules.mcp import token
from app.modules.mcp.server import build_server
from app.modules.notes import router as notes
from app.modules.projects import router as projects
from app.modules.search import router as search
from app.modules.settings import router as app_settings
from app.modules.shopping import router as shopping
from app.modules.shops import router as shops
from app.modules.tags import router as tags


def operation_id(route: APIRoute) -> str:
    # The function name, so generated hooks read like useGetHealth.
    return route.name


def create_app() -> FastAPI:
    @contextmanager
    def open_session() -> Iterator[Session]:
        # The same session the API's dependency gives (tests override it).
        provider = app.dependency_overrides.get(get_session, get_session)
        sessions = provider()
        try:
            yield next(sessions)
        finally:
            sessions.close()

    # MCP at /mcp. Stateless JSON responses: nothing to keep between requests, and
    # plain responses pass through any proxy. Its own Host check is off because it would
    # reject the HA box's LAN address; the token (core/access.py) does that job.
    mcp_server = build_server(open_session)
    mcp_app = mcp_server.streamable_http_app(
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )

    app = FastAPI(
        title="Shelf-help",
        docs_url="/api/docs",
        redoc_url=None,
        openapi_url="/api/openapi.json",
        generate_unique_id_function=operation_id,
        lifespan=lambda _app: mcp_server.session_manager.run(),
    )

    api = APIRouter(prefix="/api")
    api.include_router(health.router)
    api.include_router(locations.router)
    api.include_router(items.router)
    api.include_router(projects.router)
    api.include_router(notes.router)
    api.include_router(tags.router)
    api.include_router(shops.router)
    api.include_router(shopping.router)
    api.include_router(links.router)
    api.include_router(attachments.router)
    api.include_router(inbox.router)
    api.include_router(search.router)
    api.include_router(app_settings.router)
    api.include_router(dashboard.router)
    api.include_router(mcp.router)

    app.include_router(api)
    app.router.routes.extend(mcp_app.routes)
    register_error_handlers(app)
    app.add_middleware(
        AccessMiddleware, trusted_clients=settings.trusted_clients, token_is_valid=token.is_valid
    )
    # Last, so its catch-all route doesn't shadow the API.
    mount_frontend(app, settings.frontend_dist)
    return app
