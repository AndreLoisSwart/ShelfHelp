from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.core.schemas import Name, reject_null
from app.modules.items.schemas import ProjectRef


class NoteSummary(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, json_schema_serialization_defaults_required=True
    )

    id: int
    title: str
    project: ProjectRef | None
    in_inbox: bool
    updated_at: datetime
    # The start of the body as plain text, for lists.
    excerpt: str = ""


class NoteDetail(NoteSummary):
    body_md: str
    created_at: datetime


class NoteCreate(BaseModel):
    title: Name
    project_id: int | None = None
    body_md: str = ""


class NoteUpdate(BaseModel):
    """Only the fields sent are changed. project_id: null removes it from its project."""

    title: Name | None = None
    project_id: int | None = None
    body_md: str | None = None
    in_inbox: bool | None = None

    _not_null = field_validator("title", "body_md", "in_inbox")(reject_null)
