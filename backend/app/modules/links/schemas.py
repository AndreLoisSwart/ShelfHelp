from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.schemas import reject_null
from app.modules.owners import OwnerType


def _web_url(value: str | None) -> str | None:
    """Only http(s): a javascript: or data: link would run code when clicked."""
    if value is None:
        return None
    value = value.strip()
    parsed = urlparse(value)
    if parsed.scheme.lower() not in ("http", "https") or not parsed.netloc:
        raise ValueError("Only web links starting with http:// or https:// are allowed")
    return value


Url = Field(max_length=2000)
Title = Field(default="", max_length=200)


class LinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    title: str


class LinkCreate(BaseModel):
    owner_type: OwnerType
    owner_id: int
    url: str = Url
    title: str = Title

    _url = field_validator("url")(_web_url)


class LinkUpdate(BaseModel):
    """Only the fields sent are changed."""

    url: str | None = Field(default=None, max_length=2000)
    title: str | None = Field(default=None, max_length=200)

    _not_null = field_validator("url", "title")(reject_null)
    _url = field_validator("url")(_web_url)
