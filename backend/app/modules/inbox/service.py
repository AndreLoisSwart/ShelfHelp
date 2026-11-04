from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.items.models import Item
from app.modules.notes.models import Note
from app.modules.projects.models import Project

# Quick-add sets in_inbox on create; "Done" clears it with a normal update.
MODELS = (Item, Project, Note)


def in_inbox[T: (Item, Project, Note)](session: Session, model: type[T]) -> list[T]:
    """Newest first."""
    query = select(model).where(model.in_inbox).order_by(model.created_at.desc(), model.id.desc())
    return list(session.scalars(query))


def count(session: Session) -> int:
    return sum(
        session.scalar(select(func.count()).select_from(model).where(model.in_inbox)) or 0
        for model in MODELS
    )
