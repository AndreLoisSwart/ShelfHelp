from fastapi import APIRouter

from app.core.db import SessionDep
from app.modules.notes import service
from app.modules.notes.models import Note
from app.modules.notes.schemas import NoteCreate, NoteDetail, NoteSummary, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


def _summary(note: Note) -> NoteSummary:
    return NoteSummary.model_validate(note).model_copy(
        update={"excerpt": service.excerpt(note.body_md)}
    )


def _detail(note: Note) -> NoteDetail:
    return NoteDetail.model_validate(note).model_copy(
        update={"excerpt": service.excerpt(note.body_md)}
    )


@router.get("")
def list_notes(
    session: SessionDep, project_id: int | None = None, no_project: bool = False
) -> list[NoteSummary]:
    """Most recently updated first. no_project lists only notes without a project."""
    return [_summary(note) for note in service.list_notes(session, project_id, no_project)]


@router.post("", status_code=201)
def create_note(data: NoteCreate, session: SessionDep) -> NoteDetail:
    return _detail(service.create_note(session, data))


@router.get("/{note_id}")
def get_note(note_id: int, session: SessionDep) -> NoteDetail:
    return _detail(service.get_note(session, note_id))


@router.patch("/{note_id}")
def update_note(note_id: int, data: NoteUpdate, session: SessionDep) -> NoteDetail:
    return _detail(service.update_note(session, note_id, data))


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, session: SessionDep) -> None:
    service.delete_note(session, note_id)
