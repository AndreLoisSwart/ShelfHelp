from fastapi import APIRouter

from app.core.db import SessionDep
from app.modules.inbox import service
from app.modules.inbox.schemas import Inbox, InboxCount
from app.modules.items.models import Item
from app.modules.items.schemas import ItemSummary
from app.modules.notes import service as notes
from app.modules.notes.models import Note
from app.modules.notes.schemas import NoteSummary
from app.modules.projects.models import Project
from app.modules.projects.summaries import summaries
from app.modules.tasks import router as tasks
from app.modules.tasks.models import Task

router = APIRouter(prefix="/inbox", tags=["inbox"])


@router.get("")
def get_inbox(session: SessionDep) -> Inbox:
    """Quick-added records still waiting to be sorted, newest first."""
    return Inbox(
        items=[ItemSummary.model_validate(i) for i in service.in_inbox(session, Item)],
        projects=summaries(session, service.in_inbox(session, Project)),
        tasks=[tasks.summary(t) for t in service.in_inbox(session, Task)],
        notes=[
            NoteSummary.model_validate(n).model_copy(update={"excerpt": notes.excerpt(n.body_md)})
            for n in service.in_inbox(session, Note)
        ],
    )


@router.get("/count")
def get_inbox_count(session: SessionDep) -> InboxCount:
    return InboxCount(count=service.count(session))
