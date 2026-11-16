from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base, UTCDateTime, utcnow
from app.modules.items.models import Item
from app.modules.projects.models import Project
from app.modules.tags.models import Tag

task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

# Items are linked to tasks, never owned by them.
task_items = Table(
    "task_items",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("item_id", ForeignKey("items.id", ondelete="CASCADE"), primary_key=True, index=True),
)


class Task(Base):
    """Something to do, in a project or standalone. A project's first open task is its
    next step."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    # Deleting a project deletes its tasks.
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    # Order among the tasks of its project, or among standalone tasks. Lowest first.
    position: Mapped[int] = mapped_column(default=0)
    # Set when ticked off, cleared when reopened.
    done_at: Mapped[datetime | None] = mapped_column(UTCDateTime)
    in_inbox: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)

    project: Mapped[Project | None] = relationship(lazy="joined")
    tags: Mapped[list[Tag]] = relationship(
        secondary=task_tags, order_by=lambda: func.lower(Tag.name), lazy="selectin"
    )
    items: Mapped[list[Item]] = relationship(
        secondary=task_items, order_by=lambda: func.lower(Item.name), lazy="selectin"
    )
