from typing import Annotated

from fastapi import APIRouter, Query

from app.core.db import SessionDep
from app.modules.tasks import service
from app.modules.tasks.models import Task
from app.modules.tasks.schemas import (
    TaskCreate,
    TaskDetail,
    TaskOrder,
    TaskSummary,
    TaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def summary(task: Task) -> TaskSummary:
    return TaskSummary.model_validate(task).model_copy(
        update={"readiness": service.readiness(task)}
    )


def _detail(task: Task) -> TaskDetail:
    return TaskDetail.model_validate(task).model_copy(update={"readiness": service.readiness(task)})


@router.get("")
def list_tasks(
    session: SessionDep,
    project_id: int | None = None,
    no_project: bool = False,
    tag_id: Annotated[list[int] | None, Query()] = None,
    done: bool | None = None,
) -> list[TaskSummary]:
    """Open tasks first, in order; then done ones, most recently done first.
    no_project lists only standalone tasks. Several tag_id values match any of them."""
    return [summary(t) for t in service.list_tasks(session, project_id, no_project, tag_id, done)]


@router.post("", status_code=201)
def create_task(data: TaskCreate, session: SessionDep) -> TaskDetail:
    """Added at the bottom of its project's tasks (or the standalone ones)."""
    return _detail(service.create_task(session, data))


@router.put("/order")
def reorder_tasks(data: TaskOrder, session: SessionDep) -> list[TaskSummary]:
    """Sets the order of open tasks. Returns them all, in their new order."""
    return [summary(task) for task in service.reorder(session, data)]


@router.get("/{task_id}")
def get_task(task_id: int, session: SessionDep) -> TaskDetail:
    return _detail(service.get_task(session, task_id))


@router.patch("/{task_id}")
def update_task(task_id: int, data: TaskUpdate, session: SessionDep) -> TaskDetail:
    return _detail(service.update_task(session, task_id, data))


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, session: SessionDep) -> None:
    service.delete_task(session, task_id)
