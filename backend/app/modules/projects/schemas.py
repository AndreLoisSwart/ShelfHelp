from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.schemas import Name, reject_null
from app.modules.items.schemas import ItemSummary
from app.modules.projects.models import ProjectStatus, Requirement
from app.modules.tags.schemas import TagRef


class Readiness(BaseModel):
    """Linked items on hand (status have or low), out of all linked items."""

    # Always sent, so the generated client types these fields as present.
    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    ready: int = 0
    required: int = 0
    nice_ready: int = 0
    nice_to_have: int = 0


class ProjectSummary(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, json_schema_serialization_defaults_required=True
    )

    id: int
    name: str
    status: ProjectStatus
    next_step: str
    in_inbox: bool
    tags: list[TagRef]
    last_touched_at: datetime
    readiness: Readiness = Readiness()


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
    in_inbox: bool = False


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


class ProjectItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item: ItemSummary
    requirement: Requirement
    note: str


class ProjectItemLink(BaseModel):
    """Links an item, or updates the link if it's already linked."""

    requirement: Requirement = Requirement.REQUIRED
    note: str = Field(default="", max_length=200)
