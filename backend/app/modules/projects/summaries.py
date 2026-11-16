"""Project summaries with everything computed on read: readiness and the next step.

Separate from the service, since the next step comes from the tasks module, which
itself uses the projects service."""

from sqlalchemy.orm import Session

from app.modules.projects import service
from app.modules.projects.models import Project
from app.modules.projects.schemas import NextTask, ProjectDetail, ProjectSummary, TaskCounts
from app.modules.tasks import service as tasks


def _computed(session: Session, projects: list[Project]) -> dict[int, dict]:
    ids = [project.id for project in projects]
    readiness = service.readiness(session, ids)
    next_tasks = tasks.next_tasks(session, ids)
    counts = tasks.task_counts(session, ids)
    return {
        project_id: {
            "readiness": readiness[project_id],
            "next_task": (
                NextTask.model_validate(next_tasks[project_id])
                if project_id in next_tasks
                else None
            ),
            "task_counts": TaskCounts(
                open=counts.get(project_id, (0, 0))[0], done=counts.get(project_id, (0, 0))[1]
            ),
        }
        for project_id in ids
    }


def summaries(session: Session, projects: list[Project]) -> list[ProjectSummary]:
    computed = _computed(session, projects)
    return [
        ProjectSummary.model_validate(project).model_copy(update=computed[project.id])
        for project in projects
    ]


def detail(session: Session, project: Project) -> ProjectDetail:
    computed = _computed(session, [project])[project.id]
    computed["suggested_tags"] = service.suggested_tags(session, project)
    return ProjectDetail.model_validate(project).model_copy(update=computed)
