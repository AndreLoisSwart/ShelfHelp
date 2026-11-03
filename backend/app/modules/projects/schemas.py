from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.schemas import Name, reject_null
from app.modules.projects.models import ProjectStatus
from app.modules.tags.schemas import TagRef


class ProjectSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: ProjectStatus
    next_step: str
    in_inbox: bool
    tags: list[TagRef]
    last_touched_at: datetime


class ProjectDetail(ProjectSummary):
    description_md: str
    created_at: datetime
    updated_at: datetime


class ProjectCreate(BaseModel):
    name: Name
    status: ProjectStatus = ProjectStatus.SOMEDAY
    description_md: str = ""
    next_step: str = Field(default="", max_length=500)
    tag_ids: list[int] = []


class ProjectUpdate(BaseModel):
    """Only the fields sent are changed."""

    name: Name | None = None
    status: ProjectStatus | None = None
    description_md: str | None = None
    next_step: str | None = Field(default=None, max_length=500)
    tag_ids: list[int] | None = None
    in_inbox: bool | None = None

    _not_null = field_validator(
        "name", "status", "description_md", "next_step", "tag_ids", "in_inbox"
    )(reject_null)
