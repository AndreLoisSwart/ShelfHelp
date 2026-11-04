from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.schemas import reject_null


class SettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stale_after_days: int


class SettingsUpdate(BaseModel):
    """Only the fields sent are changed."""

    # From a week to a year.
    stale_after_days: int | None = Field(default=None, ge=7, le=365)

    _not_null = field_validator("stale_after_days")(reject_null)
