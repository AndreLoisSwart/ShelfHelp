from datetime import datetime

from pydantic import BaseModel

from app.modules.items.schemas import ItemSummary
from app.modules.projects.models import ProjectStatus
from app.modules.projects.schemas import ProjectSummary


class StaleProject(BaseModel):
    id: int
    name: str
    status: ProjectStatus
    last_touched_at: datetime


class Dashboard(BaseModel):
    # Active projects, most recently touched first.
    active: list[ProjectSummary]
    # Out, then low. Capped; running_low_total counts them all.
    running_low: list[ItemSummary]
    running_low_total: int
    # Active or paused projects untouched for longer than stale_after_days, oldest first.
    stale: list[StaleProject]
    stale_after_days: int
