from pydantic import BaseModel, field_validator

from app.core.schemas import Name, reject_null
from app.modules.tags.schemas import TagRef


class LocationOut(BaseModel):
    id: int
    name: str
    parent_id: int | None
    # Items stored directly here, not in sub-locations.
    item_count: int
    # Given to items put here or in a sub-location.
    tags: list[TagRef]


class LocationCreate(BaseModel):
    name: Name
    parent_id: int | None = None
    tag_ids: list[int] = []


class LocationUpdate(BaseModel):
    """Only the fields sent are changed. parent_id: null moves it to the top level."""

    name: Name | None = None
    parent_id: int | None = None
    # Replaces its tags. Only items put here from now on get them; see tag_items.
    tag_ids: list[int] | None = None

    _not_null = field_validator("name", "tag_ids")(reject_null)


class TaggedCount(BaseModel):
    count: int
