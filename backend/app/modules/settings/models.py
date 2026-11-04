from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

DEFAULT_STALE_AFTER_DAYS = 21


class AppSettings(Base):
    """App-wide preferences, shared by every device. A single row, id 1."""

    __tablename__ = "app_settings"
    __table_args__ = (CheckConstraint("id = 1", name="single_row"),)

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    # An active or paused project untouched for longer than this is stale.
    stale_after_days: Mapped[int] = mapped_column(default=DEFAULT_STALE_AFTER_DAYS)
