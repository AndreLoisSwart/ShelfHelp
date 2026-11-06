from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Shop(Base):
    """Somewhere items can be bought. An item can be had from several shops."""

    __tablename__ = "shops"

    id: Mapped[int] = mapped_column(primary_key=True)
    # NOCASE: "Builders" and "builders" are the same shop.
    name: Mapped[str] = mapped_column(String(200, collation="NOCASE"), unique=True)
