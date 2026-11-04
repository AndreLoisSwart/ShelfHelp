from collections import defaultdict

from sqlalchemy import case, func, select, update
from sqlalchemy.orm import Session

from app.core.db import utcnow
from app.core.errors import NotFoundError
from app.modules.attachments import storage
from app.modules.attachments.models import Attachment
from app.modules.items.models import Item, ItemStatus
from app.modules.projects.models import Project, ProjectItem, ProjectStatus, Requirement
from app.modules.projects.schemas import (
    ProjectCreate,
    ProjectItemLink,
    ProjectUpdate,
    Readiness,
)
from app.modules.tags import service as tags
from app.modules.tags.models import Tag


def get_project(session: Session, project_id: int) -> Project:
    project = session.get(Project, project_id)
    if project is None:
        raise NotFoundError(f"Project {project_id} not found")
    return project


def touch(project: Project) -> None:
    """Marks the project as worked on. Call whenever it or anything attached to it changes:
    the project itself, its notes, item links, links or attachments."""
    project.last_touched_at = utcnow()


def touch_projects_using(session: Session, item_id: int) -> None:
    """Touches every project the item is linked to, e.g. before the item is deleted."""
    linked = select(ProjectItem.project_id).where(ProjectItem.item_id == item_id)
    session.execute(update(Project).where(Project.id.in_(linked)).values(last_touched_at=utcnow()))


# Readiness counts an item as on hand while it is low: it's there, just running out.
ON_HAND = (ItemStatus.HAVE, ItemStatus.LOW)


def readiness(session: Session, project_ids: list[int]) -> dict[int, Readiness]:
    """Computed on every read, never stored."""
    on_hand = func.sum(case((Item.status.in_(ON_HAND), 1), else_=0))
    rows = session.execute(
        select(ProjectItem.project_id, ProjectItem.requirement, func.count(), on_hand)
        .join(Item)
        .where(ProjectItem.project_id.in_(project_ids))
        .group_by(ProjectItem.project_id, ProjectItem.requirement)
    )
    result: dict[int, Readiness] = defaultdict(Readiness)
    for project_id, requirement, total, ready in rows:
        counts = result[project_id]
        if requirement == Requirement.REQUIRED:
            counts.required, counts.ready = total, ready
        else:
            counts.nice_to_have, counts.nice_ready = total, ready
    return result


def list_projects(
    session: Session,
    statuses: list[ProjectStatus] | None = None,
    tag_ids: list[int] | None = None,
) -> list[Project]:
    # Most recently worked on first, so stalled projects sink.
    query = select(Project).order_by(Project.last_touched_at.desc(), Project.id.desc())
    if statuses:
        query = query.where(Project.status.in_(statuses))
    if tag_ids:
        query = query.where(Project.tags.any(Tag.id.in_(tag_ids)))
    return list(session.scalars(query))


def create_project(session: Session, data: ProjectCreate) -> Project:
    project = Project(
        name=data.name,
        status=data.status,
        description_md=data.description_md,
        next_step=data.next_step.strip(),
        tags=tags.get_tags(session, data.tag_ids),
    )
    session.add(project)
    session.commit()
    return project


def update_project(session: Session, project_id: int, data: ProjectUpdate) -> Project:
    project = get_project(session, project_id)
    changes = data.model_dump(exclude_unset=True)
    if (tag_ids := changes.pop("tag_ids", None)) is not None:
        project.tags = tags.get_tags(session, tag_ids)
    if "next_step" in changes:
        changes["next_step"] = changes["next_step"].strip()
    for field, value in changes.items():
        setattr(project, field, value)
    project.updated_at = utcnow()
    touch(project)
    session.commit()
    return project


def delete_project(session: Session, project_id: int) -> None:
    project = get_project(session, project_id)
    # Its links, attachments and item links go with it (ON DELETE CASCADE), but files on
    # disk don't: remove them once the delete is committed. Its notes are kept.
    files = storage.stored_paths_of(session, Attachment.project_id, project_id)
    session.delete(project)
    session.commit()
    storage.remove_files(files)


def list_project_items(session: Session, project_id: int) -> list[ProjectItem]:
    get_project(session, project_id)
    query = (
        select(ProjectItem)
        .join(Item)
        .where(ProjectItem.project_id == project_id)
        # Required first, then by name.
        .order_by(ProjectItem.requirement != Requirement.REQUIRED, func.lower(Item.name))
    )
    return list(session.scalars(query))


def link_item(
    session: Session, project_id: int, item_id: int, data: ProjectItemLink
) -> ProjectItem:
    project = get_project(session, project_id)
    if session.get(Item, item_id) is None:
        raise NotFoundError(f"Item {item_id} not found")
    link = session.get(ProjectItem, (project_id, item_id))
    if link is None:
        link = ProjectItem(project_id=project_id, item_id=item_id)
        session.add(link)
    link.requirement = data.requirement
    link.note = data.note.strip()
    touch(project)
    session.commit()
    return link


def unlink_item(session: Session, project_id: int, item_id: int) -> None:
    project = get_project(session, project_id)
    link = session.get(ProjectItem, (project_id, item_id))
    if link is None:
        raise NotFoundError(f"Item {item_id} isn't linked to this project")
    session.delete(link)
    touch(project)
    session.commit()
