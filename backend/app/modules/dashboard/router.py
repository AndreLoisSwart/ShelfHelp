from fastapi import APIRouter

from app.core.db import SessionDep
from app.modules.dashboard import service
from app.modules.dashboard.schemas import Dashboard

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(session: SessionDep) -> Dashboard:
    return service.dashboard(session)
