from typing import Annotated

from fastapi import APIRouter, Query

from app.core.db import SessionDep
from app.modules.projects import service
from app.modules.projects.models import ProjectStatus
from app.modules.projects.schemas import (
    ProjectCreate,
    ProjectDetail,
    ProjectSummary,
    ProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("")
def list_projects(
    session: SessionDep,
    status: Annotated[list[ProjectStatus] | None, Query()] = None,
    tag_id: Annotated[list[int] | None, Query()] = None,
) -> list[ProjectSummary]:
    """Most recently touched first. Several status or tag_id values match any of them."""
    projects = service.list_projects(session, status, tag_id)
    return [ProjectSummary.model_validate(project) for project in projects]


@router.post("", status_code=201)
def create_project(data: ProjectCreate, session: SessionDep) -> ProjectDetail:
    return ProjectDetail.model_validate(service.create_project(session, data))


@router.get("/{project_id}")
def get_project(project_id: int, session: SessionDep) -> ProjectDetail:
    return ProjectDetail.model_validate(service.get_project(session, project_id))


@router.patch("/{project_id}")
def update_project(project_id: int, data: ProjectUpdate, session: SessionDep) -> ProjectDetail:
    return ProjectDetail.model_validate(service.update_project(session, project_id, data))


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, session: SessionDep) -> None:
    service.delete_project(session, project_id)
