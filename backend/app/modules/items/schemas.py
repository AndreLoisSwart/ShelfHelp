from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.core.schemas import Name, reject_null
from app.modules.items.models import ItemStatus
from app.modules.projects.models import ProjectStatus, Requirement
from app.modules.shops.schemas import ShopRef
from app.modules.tags.schemas import TagRef


class ItemRef(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, json_schema_serialization_defaults_required=True
    )

    id: int
    name: str


class ItemSummary(ItemRef):
    status: ItemStatus
    parent_id: int | None
    location_id: int | None
    in_inbox: bool
    tags: list[TagRef]
    shops: list[ShopRef]


class ProjectRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: ProjectStatus


class ItemProjectOut(BaseModel):
    project: ProjectRef
    requirement: Requirement
    note: str


class ItemDetail(ItemSummary):
    description: str
    parent: ItemRef | None
    children: list[ItemSummary]
    projects: list[ItemProjectOut] = []
    created_at: datetime
    updated_at: datetime


class ItemCreate(BaseModel):
    name: Name
    status: ItemStatus = ItemStatus.HAVE
    description: str = ""
    parent_id: int | None = None
    location_id: int | None = None
    tag_ids: list[int] = []
    shop_ids: list[int] = []
    in_inbox: bool = False


class ItemUpdate(BaseModel):
    """Only the fields sent are changed. parent_id or location_id: null clears them."""

    name: Name | None = None
    status: ItemStatus | None = None
    description: str | None = None
    parent_id: int | None = None
    location_id: int | None = None
    tag_ids: list[int] | None = None
    shop_ids: list[int] | None = None
    in_inbox: bool | None = None

    _not_null = field_validator("name", "status", "description", "tag_ids", "shop_ids", "in_inbox")(
        reject_null
    )
