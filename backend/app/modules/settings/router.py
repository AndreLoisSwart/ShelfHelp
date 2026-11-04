from fastapi import APIRouter

from app.core.db import SessionDep
from app.modules.settings import service
from app.modules.settings.schemas import SettingsOut, SettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("")
def get_settings(session: SessionDep) -> SettingsOut:
    return SettingsOut.model_validate(service.get_settings(session))


@router.patch("")
def update_settings(data: SettingsUpdate, session: SessionDep) -> SettingsOut:
    return SettingsOut.model_validate(service.update_settings(session, data))
