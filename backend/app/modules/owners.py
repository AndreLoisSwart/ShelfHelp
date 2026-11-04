"""Links and attachments each belong to exactly one project, item or note.

Shared by the links and attachments modules: checks the owner exists, filters by owner,
and touches the project the change counts towards.
"""

from enum import StrEnum

from sqlalchemy import ColumnElement
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.modules.items.models import Item
from app.modules.notes.models import Note
from app.modules.projects import service as projects
from app.modules.projects.models import Project


class OwnerType(StrEnum):
    PROJECT = "project"
    ITEM = "item"
    NOTE = "note"


MODELS = {OwnerType.PROJECT: Project, OwnerType.ITEM: Item, OwnerType.NOTE: Note}


def owner_column(model, owner_type: OwnerType):
    return getattr(model, f"{owner_type}_id")


def owner_filter(model, owner_type: OwnerType, owner_id: int) -> ColumnElement[bool]:
    return owner_column(model, owner_type) == owner_id


def check_owner(session: Session, owner_type: OwnerType, owner_id: int) -> None:
    if session.get(MODELS[owner_type], owner_id) is None:
        raise NotFoundError(f"{owner_type.capitalize()} {owner_id} not found")


def owner_of(record) -> tuple[OwnerType, int]:
    for owner_type in OwnerType:
        if (owner_id := getattr(record, f"{owner_type}_id")) is not None:
            return owner_type, owner_id
    raise ValueError("record has no owner")


def touch_owner(session: Session, owner_type: OwnerType, owner_id: int) -> None:
    """A project's own links and files touch it, and so do those of its notes."""
    if owner_type == OwnerType.PROJECT:
        projects.touch(projects.get_project(session, owner_id))
    elif owner_type == OwnerType.NOTE:
        note = session.get(Note, owner_id)
        if note is not None and note.project is not None:
            projects.touch(note.project)
