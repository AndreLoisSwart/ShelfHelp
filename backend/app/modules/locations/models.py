from sqlalchemy import Column, ForeignKey, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.modules.tags.models import Tag

location_tags = Table(
    "location_tags",
    Base.metadata,
    Column("location_id", ForeignKey("locations.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Location(Base):
    """A tree. Top-level locations (no parent) are zones, e.g. Home and Workshop."""

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"), index=True
    )
    # Given to items when they're put here or in a sub-location. Copied, not linked:
    # the item can drop them, and changing these doesn't change existing items.
    tags: Mapped[list[Tag]] = relationship(
        secondary=location_tags, order_by=lambda: func.lower(Tag.name), lazy="selectin"
    )
