import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import utcnow
from app.core.errors import NotFoundError
from app.modules.attachments import storage
from app.modules.attachments.models import Attachment
from app.modules.notes.models import Note
from app.modules.notes.schemas import NoteCreate, NoteUpdate
from app.modules.projects import service as projects

EXCERPT_LENGTH = 140
# Markdown syntax that reads as noise in a one-line preview.
_MARKDOWN_NOISE = re.compile(
    # Line starts: checkbox (before plain bullets), heading, bullet, number, quote.
    r"^\s*([-*+] \[[ xX]\]|#{1,6}|[-*+]|\d+\.|>)\s+"
    # Emphasis and code marks, and links (keeping their text).
    r"|[*_`~]|\[([^\]]*)\]\([^)]*\)",
    re.M,
)


def excerpt(body_md: str) -> str:
    text = _MARKDOWN_NOISE.sub(lambda m: m.group(2) or "", body_md)
    text = " ".join(text.split())
    return text if len(text) <= EXCERPT_LENGTH else text[: EXCERPT_LENGTH - 1].rstrip() + "…"


def get_note(session: Session, note_id: int) -> Note:
    note = session.get(Note, note_id)
    if note is None:
        raise NotFoundError(f"Note {note_id} not found")
    return note


def _touch_project(session: Session, project_id: int | None) -> None:
    if project_id is not None:
        projects.touch(projects.get_project(session, project_id))


def list_notes(
    session: Session, project_id: int | None = None, no_project: bool = False
) -> list[Note]:
    query = select(Note).order_by(Note.updated_at.desc(), Note.id.desc())
    if project_id is not None:
        query = query.where(Note.project_id == project_id)
    elif no_project:
        query = query.where(Note.project_id.is_(None))
    return list(session.scalars(query))


def create_note(session: Session, data: NoteCreate) -> Note:
    _touch_project(session, data.project_id)
    note = Note(title=data.title, project_id=data.project_id, body_md=data.body_md)
    session.add(note)
    session.commit()
    return note


def update_note(session: Session, note_id: int, data: NoteUpdate) -> Note:
    note = get_note(session, note_id)
    changes = data.model_dump(exclude_unset=True)
    _touch_project(session, note.project_id)
    if "project_id" in changes:
        # Moving between projects changes both. Set the relationship, not just the id,
        # so the loaded project is the new one.
        project_id = changes.pop("project_id")
        note.project = None if project_id is None else projects.get_project(session, project_id)
        _touch_project(session, project_id)
    for field, value in changes.items():
        setattr(note, field, value)
    note.updated_at = utcnow()
    session.commit()
    return note


def delete_note(session: Session, note_id: int) -> None:
    note = get_note(session, note_id)
    _touch_project(session, note.project_id)
    # Links and attachments go with it (ON DELETE CASCADE); remove the files after.
    files = storage.stored_paths_of(session, Attachment.note_id, note_id)
    session.delete(note)
    session.commit()
    storage.remove_files(files)
