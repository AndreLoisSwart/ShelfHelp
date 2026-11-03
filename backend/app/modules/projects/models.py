from datetime import datetime
from enum import StrEnum

from sqlalchemy import Column, Enum, ForeignKey, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base, UTCDateTime, utcnow
from app.modules.items.models import Item
from app.modules.tags.models import Tag


class ProjectStatus(StrEnum):
    SOMEDAY = "someday"
    PLANNED = "planned"
    ACTIVE = "active"
    PAUSED = "paused"
    DONE = "done"
    ABANDONED = "abandoned"


class Requirement(StrEnum):
    REQUIRED = "required"
    NICE_TO_HAVE = "nice_to_have"


project_tags = Table(
    "project_tags",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description_md: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(
            ProjectStatus,
            name="status",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda e: [m.value for m in e],
        )
    )
    next_step: Mapped[str] = mapped_column(String(500), default="")
    in_inbox: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    # Set by the service layer when the project or anything attached to it changes.
    last_touched_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow, index=True)

    tags: Mapped[list[Tag]] = relationship(
        secondary=project_tags, order_by=lambda: func.lower(Tag.name), lazy="selectin"
    )


class ProjectItem(Base):
    """An item linked to a project. Items are created standalone, then linked."""

    __tablename__ = "project_items"

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    requirement: Mapped[Requirement] = mapped_column(
        Enum(
            Requirement,
            name="requirement",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda e: [m.value for m in e],
        )
    )
    note: Mapped[str] = mapped_column(String(200), default="")

    item: Mapped[Item] = relationship(lazy="joined")
