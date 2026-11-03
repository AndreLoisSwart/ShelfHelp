from pydantic import BaseModel, field_validator

from app.core.schemas import Name, reject_null


class LocationOut(BaseModel):
    id: int
    name: str
    parent_id: int | None
    # Items stored directly here, not in sub-locations.
    item_count: int


class LocationCreate(BaseModel):
    name: Name
    parent_id: int | None = None


class LocationUpdate(BaseModel):
    """Only the fields sent are changed. parent_id: null moves it to the top level."""

    name: Name | None = None
    parent_id: int | None = None

    _not_null = field_validator("name")(reject_null)
