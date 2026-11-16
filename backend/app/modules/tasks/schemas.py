from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.schemas import Name, reject_null
from app.modules.items.schemas import ItemSummary, ProjectRef
from app.modules.tags.schemas import TagRef


class TaskReadiness(BaseModel):
    """Linked items on hand (status have or low), out of all linked items."""

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    ready: int = 0
    total: int = 0


class TaskSummary(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, json_schema_serialization_defaults_required=True
    )

    id: int
    title: str
    project: ProjectRef | None
    position: int
    done_at: datetime | None
    in_inbox: bool
    tags: list[TagRef]
    readiness: TaskReadiness = TaskReadiness()


class TaskDetail(TaskSummary):
    description: str
    items: list[ItemSummary]
    created_at: datetime
    updated_at: datetime


class TaskCreate(BaseModel):
    title: Name
    description: str = ""
    project_id: int | None = None
    tag_ids: list[int] = []
    item_ids: list[int] = []
    in_inbox: bool = False


class TaskUpdate(BaseModel):
    """Only the fields sent are changed. project_id: null makes it standalone.
    done: true ticks it off, false reopens it."""

    title: Name | None = None
    description: str | None = None
    project_id: int | None = None
    tag_ids: list[int] | None = None
    item_ids: list[int] | None = None
    done: bool | None = None
    in_inbox: bool | None = None

    _not_null = field_validator("title", "description", "tag_ids", "item_ids", "done", "in_inbox")(
        reject_null
    )


class TaskOrder(BaseModel):
    """Open tasks of one project (or the standalone ones, project_id null), in their new
    order. Open tasks left out keep their order, after these."""

    project_id: int | None = None
    task_ids: list[int] = Field(min_length=1)
