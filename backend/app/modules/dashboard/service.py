"""The dashboard is computed on request, like readiness and the shopping list."""

from datetime import timedelta

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.core.db import utcnow
from app.modules.dashboard.schemas import Dashboard, StaleProject
from app.modules.items.models import Item, ItemStatus
from app.modules.items.schemas import ItemSummary
from app.modules.projects import service as projects
from app.modules.projects.models import Project, ProjectStatus
from app.modules.projects.schemas import ProjectSummary
from app.modules.settings import service as settings

RUNNING_LOW_LIMIT = 6
RUNNING_LOW = (ItemStatus.OUT, ItemStatus.LOW)
CAN_GO_STALE = (ProjectStatus.ACTIVE, ProjectStatus.PAUSED)


def stale_projects(session: Session, stale_after_days: int) -> list[Project]:
    cutoff = utcnow() - timedelta(days=stale_after_days)
    query = (
        select(Project)
        .where(Project.status.in_(CAN_GO_STALE), Project.last_touched_at < cutoff)
        .order_by(Project.last_touched_at, Project.id)
    )
    return list(session.scalars(query))


def dashboard(session: Session) -> Dashboard:
    active = projects.list_projects(session, [ProjectStatus.ACTIVE])
    readiness = projects.readiness(session, [p.id for p in active])

    low_filter = Item.status.in_(RUNNING_LOW)
    running_low = session.scalars(
        select(Item)
        .where(low_filter)
        .order_by(case((Item.status == ItemStatus.OUT, 0), else_=1), func.lower(Item.name))
        .limit(RUNNING_LOW_LIMIT)
    )
    running_low_total = session.scalar(select(func.count()).select_from(Item).where(low_filter))

    stale_after_days = settings.get_settings(session).stale_after_days
    return Dashboard(
        active=[
            ProjectSummary.model_validate(p).model_copy(update={"readiness": readiness[p.id]})
            for p in active
        ],
        running_low=[ItemSummary.model_validate(item) for item in running_low],
        running_low_total=running_low_total or 0,
        stale=[
            StaleProject(id=p.id, name=p.name, status=p.status, last_touched_at=p.last_touched_at)
            for p in stale_projects(session, stale_after_days)
        ],
        stale_after_days=stale_after_days,
    )
