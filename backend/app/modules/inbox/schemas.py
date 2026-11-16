from pydantic import BaseModel

from app.modules.items.schemas import ItemSummary
from app.modules.notes.schemas import NoteSummary
from app.modules.projects.schemas import ProjectSummary
from app.modules.tasks.schemas import TaskSummary


class Inbox(BaseModel):
    items: list[ItemSummary]
    projects: list[ProjectSummary]
    tasks: list[TaskSummary]
    notes: list[NoteSummary]


class InboxCount(BaseModel):
    count: int
