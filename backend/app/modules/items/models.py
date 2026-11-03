from datetime import datetime
from enum import StrEnum

from sqlalchemy import Column, Enum, ForeignKey, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base, UTCDateTime, utcnow
from app.modules.tags.models import Tag


class ItemStatus(StrEnum):
    HAVE = "have"
    LOW = "low"
    OUT = "out"
    NEED = "need"


item_tags = Table(
    "item_tags",
    Base.metadata,
    Column("item_id", ForeignKey("items.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[ItemStatus] = mapped_column(
        Enum(
            ItemStatus,
            name="status",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda e: [m.value for m in e],
        )
    )
    # Deleting a parent makes its children top-level items.
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("items.id", ondelete="SET NULL"), index=True
    )
    # For a `need` item, where it will live. That decides its shopping list.
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"), index=True
    )
    in_inbox: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)

    parent: Mapped["Item | None"] = relationship(remote_side=[id], back_populates="children")
    children: Mapped[list["Item"]] = relationship(
        back_populates="parent", order_by=lambda: func.lower(Item.name)
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary=item_tags, order_by=lambda: func.lower(Tag.name), lazy="selectin"
    )
