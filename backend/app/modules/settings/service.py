from sqlalchemy.orm import Session

from app.modules.settings.models import AppSettings
from app.modules.settings.schemas import SettingsUpdate


def get_settings(session: Session) -> AppSettings:
    """The settings row, created with the defaults the first time it's needed."""
    settings = session.get(AppSettings, 1)
    if settings is None:
        settings = AppSettings(id=1)
        session.add(settings)
        session.commit()
    return settings


def update_settings(session: Session, data: SettingsUpdate) -> AppSettings:
    settings = get_settings(session)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    session.commit()
    return settings
