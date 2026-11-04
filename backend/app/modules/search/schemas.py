from pydantic import BaseModel

from app.modules.items.models import ItemStatus
from app.modules.projects.models import ProjectStatus


class SearchHit(BaseModel):
    """title and snippet wrap each matched word in \\u0002 and \\u0003."""

    id: int
    title: str
    # The best-matching stretch of the body, as plain text.
    snippet: str


class ProjectHit(SearchHit):
    status: ProjectStatus


class ItemHit(SearchHit):
    status: ItemStatus


class SearchResults(BaseModel):
    projects: list[ProjectHit]
    items: list[ItemHit]
    notes: list[SearchHit]
