from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base, one_owner_constraint


class Link(Base):
    __tablename__ = "links"
    __table_args__ = (one_owner_constraint(),)

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(2000))
    title: Mapped[str] = mapped_column(String(200), default="")
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    item_id: Mapped[int | None] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"), index=True
    )
    note_id: Mapped[int | None] = mapped_column(
        ForeignKey("notes.id", ondelete="CASCADE"), index=True
    )
