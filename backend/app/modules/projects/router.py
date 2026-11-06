from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy.orm import Session

from app.core.db import SessionDep
from app.modules.projects import service
from app.modules.projects.models import Project, ProjectStatus
from app.modules.projects.schemas import (
    ProjectCreate,
    ProjectDetail,
    ProjectItemLink,
    ProjectItemOut,
    ProjectSummary,
    ProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["projects"])


def _detail(session: Session, project: Project) -> ProjectDetail:
    readiness = service.readiness(session, [project.id])[project.id]
    suggested = service.suggested_tags(session, project)
    return ProjectDetail.model_validate(project).model_copy(
        update={"readiness": readiness, "suggested_tags": suggested}
    )


@router.get("")
def list_projects(
    session: SessionDep,
    status: Annotated[list[ProjectStatus] | None, Query()] = None,
    tag_id: Annotated[list[int] | None, Query()] = None,
) -> list[ProjectSummary]:
    """Most recently touched first. Several status or tag_id values match any of them."""
    projects = service.list_projects(session, status, tag_id)
    readiness = service.readiness(session, [project.id for project in projects])
    return [
        ProjectSummary.model_validate(project).model_copy(
            update={"readiness": readiness[project.id]}
        )
        for project in projects
    ]


@router.post("", status_code=201)
def create_project(data: ProjectCreate, session: SessionDep) -> ProjectDetail:
    return _detail(session, service.create_project(session, data))


@router.get("/{project_id}")
def get_project(project_id: int, session: SessionDep) -> ProjectDetail:
    return _detail(session, service.get_project(session, project_id))


@router.patch("/{project_id}")
def update_project(project_id: int, data: ProjectUpdate, session: SessionDep) -> ProjectDetail:
    return _detail(session, service.update_project(session, project_id, data))


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, session: SessionDep) -> None:
    service.delete_project(session, project_id)


@router.get("/{project_id}/items")
def list_project_items(project_id: int, session: SessionDep) -> list[ProjectItemOut]:
    """Required items first, then by name."""
    links = service.list_project_items(session, project_id)
    return [ProjectItemOut.model_validate(link) for link in links]


@router.put("/{project_id}/items/{item_id}")
def link_project_item(
    project_id: int, item_id: int, data: ProjectItemLink, session: SessionDep
) -> ProjectItemOut:
    """Links the item, or updates its requirement and note if it's already linked."""
    return ProjectItemOut.model_validate(service.link_item(session, project_id, item_id, data))


@router.delete("/{project_id}/items/{item_id}", status_code=204)
def unlink_project_item(project_id: int, item_id: int, session: SessionDep) -> None:
    service.unlink_item(session, project_id, item_id)
