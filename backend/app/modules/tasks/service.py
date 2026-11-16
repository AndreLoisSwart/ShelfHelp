from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.core.db import utcnow
from app.core.errors import ConflictError, NotFoundError
from app.modules.items.models import Item
from app.modules.projects import service as projects
from app.modules.projects.models import Project
from app.modules.tags import service as tags
from app.modules.tasks.models import Task, task_tags
from app.modules.tasks.schemas import TaskCreate, TaskOrder, TaskReadiness, TaskUpdate


def get_task(session: Session, task_id: int) -> Task:
    task = session.get(Task, task_id)
    if task is None:
        raise NotFoundError(f"Task {task_id} not found")
    return task


def readiness(task: Task) -> TaskReadiness:
    """Computed on every read, never stored."""
    ready = sum(1 for item in task.items if item.status in projects.ON_HAND)
    return TaskReadiness(ready=ready, total=len(task.items))


def _get_items(session: Session, item_ids: list[int]) -> list[Item]:
    found = []
    for item_id in dict.fromkeys(item_ids):
        item = session.get(Item, item_id)
        if item is None:
            raise NotFoundError(f"Item {item_id} not found")
        found.append(item)
    return sorted(found, key=lambda item: item.name.lower())


def _in_scope(project_id: int | None):
    return Task.project_id.is_(None) if project_id is None else Task.project_id == project_id


def _next_position(session: Session, project_id: int | None) -> int:
    last = session.scalar(select(func.max(Task.position)).where(_in_scope(project_id)))
    return 0 if last is None else last + 1


def _join_project(session: Session, task: Task, project: Project | None) -> None:
    """Puts the task at the bottom of the project (or of the standalone tasks), with the
    project's tags added. Tags are only ever added, as with location tags."""
    task.project = project
    task.position = _next_position(session, project.id if project else None)
    if project is not None:
        have = {tag.id for tag in task.tags}
        added = [tag for tag in project.tags if tag.id not in have]
        task.tags = sorted(task.tags + added, key=lambda tag: tag.name.lower())
        projects.touch(project)


def list_tasks(
    session: Session,
    project_id: int | None = None,
    no_project: bool = False,
    tag_ids: list[int] | None = None,
    done: bool | None = None,
) -> list[Task]:
    """Open tasks first, in their order; then done tasks, most recently done first."""
    query = select(Task).order_by(
        Task.done_at.is_not(None), Task.done_at.desc(), Task.position, Task.id
    )
    if project_id is not None:
        query = query.where(Task.project_id == project_id)
    elif no_project:
        query = query.where(Task.project_id.is_(None))
    if tag_ids:
        query = query.where(Task.tags.any(task_tags.c.tag_id.in_(tag_ids)))
    if done is not None:
        query = query.where(Task.done_at.is_not(None) if done else Task.done_at.is_(None))
    return list(session.scalars(query))


def create_task(session: Session, data: TaskCreate) -> Task:
    project = None if data.project_id is None else projects.get_project(session, data.project_id)
    task = Task(
        title=data.title,
        description=data.description.strip(),
        tags=tags.get_tags(session, data.tag_ids),
        items=_get_items(session, data.item_ids),
        in_inbox=data.in_inbox,
    )
    _join_project(session, task, project)
    session.add(task)
    session.commit()
    return task


def update_task(session: Session, task_id: int, data: TaskUpdate) -> Task:
    task = get_task(session, task_id)
    changes = data.model_dump(exclude_unset=True)
    if task.project is not None:
        projects.touch(task.project)
    if (tag_ids := changes.pop("tag_ids", None)) is not None:
        task.tags = tags.get_tags(session, tag_ids)
    if (item_ids := changes.pop("item_ids", None)) is not None:
        task.items = _get_items(session, item_ids)
    if "project_id" in changes:
        project_id = changes.pop("project_id")
        if project_id != task.project_id:
            project = None if project_id is None else projects.get_project(session, project_id)
            _join_project(session, task, project)
    if (done := changes.pop("done", None)) is not None:
        if not done:
            task.done_at = None
        elif task.done_at is None:
            task.done_at = utcnow()
    if "description" in changes:
        changes["description"] = changes["description"].strip()
    for field, value in changes.items():
        setattr(task, field, value)
    task.updated_at = utcnow()
    session.commit()
    return task


def delete_task(session: Session, task_id: int) -> None:
    task = get_task(session, task_id)
    if task.project is not None:
        projects.touch(task.project)
    session.delete(task)
    session.commit()


def reorder(session: Session, data: TaskOrder) -> list[Task]:
    """Returns the open tasks of that project (or the standalone ones), in order."""
    project = None if data.project_id is None else projects.get_project(session, data.project_id)
    open_tasks = list_tasks(
        session, data.project_id, no_project=data.project_id is None, done=False
    )
    by_id = {task.id: task for task in open_tasks}
    wanted = list(dict.fromkeys(data.task_ids))
    if missing := [task_id for task_id in wanted if task_id not in by_id]:
        where = f"project {data.project_id}" if project else "the standalone tasks"
        raise ConflictError(f"Not open tasks in {where}: {missing}")
    ordered = [by_id[task_id] for task_id in wanted]
    ordered += [task for task in open_tasks if task.id not in set(wanted)]
    for position, task in enumerate(ordered):
        task.position = position
    if project is not None:
        projects.touch(project)
    session.commit()
    return ordered


def next_tasks(session: Session, project_ids: list[int]) -> dict[int, Task]:
    """Each project's next step: its open task with the lowest position."""
    rows = session.scalars(
        select(Task)
        .where(Task.project_id.in_(project_ids), Task.done_at.is_(None))
        .order_by(Task.position.desc(), Task.id.desc())
    )
    # Ordered last first, so the first task of each project is written last.
    return {task.project_id: task for task in rows}


def task_counts(session: Session, project_ids: list[int]) -> dict[int, tuple[int, int]]:
    """Open and done tasks per project."""
    done = func.sum(case((Task.done_at.is_not(None), 1), else_=0))
    rows = session.execute(
        select(Task.project_id, func.count(), done)
        .where(Task.project_id.in_(project_ids))
        .group_by(Task.project_id)
    )
    return {project_id: (total - done_count, done_count) for project_id, total, done_count in rows}
