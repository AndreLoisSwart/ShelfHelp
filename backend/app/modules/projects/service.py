from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import utcnow
from app.core.errors import NotFoundError
from app.modules.projects.models import Project, ProjectStatus
from app.modules.projects.schemas import ProjectCreate, ProjectUpdate
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
    session.delete(get_project(session, project_id))
    session.commit()
