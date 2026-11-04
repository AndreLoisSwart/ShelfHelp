from datetime import timedelta

import pytest
from sqlalchemy import update

from app.core.db import get_session, utcnow
from app.modules.projects.models import Project


def create(api, kind, **fields):
    res = api.post(f"/api/{kind}", json=fields)
    assert res.status_code == 201, res.text
    return res.json()


@pytest.fixture
def age(api):
    """Moves a project's last touch into the past, as if untouched for that many days."""

    def _age(project_id: int, days: int) -> None:
        session = next(api.app.dependency_overrides[get_session]())
        session.execute(
            update(Project)
            .where(Project.id == project_id)
            .values(last_touched_at=utcnow() - timedelta(days=days))
        )
        session.commit()

    return _age


def names(entries):
    return [entry["name"] for entry in entries]


def test_empty(api):
    assert api.get("/api/dashboard").json() == {
        "active": [],
        "running_low": [],
        "running_low_total": 0,
        "stale": [],
        "stale_after_days": 21,
    }


def test_active_projects_most_recently_touched_first(api, age):
    older = create(api, "projects", name="Older", status="active", next_step="Sand")
    create(api, "projects", name="Newer", status="active")
    create(api, "projects", name="Someday", status="someday")
    create(api, "projects", name="Paused", status="paused")
    age(older["id"], 2)
    dashboard = api.get("/api/dashboard").json()
    assert names(dashboard["active"]) == ["Newer", "Older"]
    assert dashboard["active"][1]["next_step"] == "Sand"
    assert dashboard["active"][1]["readiness"] == {
        "ready": 0,
        "required": 0,
        "nice_ready": 0,
        "nice_to_have": 0,
    }


def test_running_low_out_first_then_by_name_and_capped(api):
    for name in ("Glue", "Sandpaper", "Screws", "Tape", "Oil", "Wax", "Rags"):
        create(api, "items", name=name, status="low")
    create(api, "items", name="Bolts", status="out")
    create(api, "items", name="Drill", status="have")
    create(api, "items", name="Saw", status="need")
    dashboard = api.get("/api/dashboard").json()
    assert names(dashboard["running_low"]) == [
        "Bolts",
        "Glue",
        "Oil",
        "Rags",
        "Sandpaper",
        "Screws",
    ]
    assert dashboard["running_low_total"] == 8


def test_stale_projects(api, age):
    old_active = create(api, "projects", name="Table saw", status="active")
    older_paused = create(api, "projects", name="Shed", status="paused")
    recent = create(api, "projects", name="Desk", status="active")
    old_someday = create(api, "projects", name="Boat", status="someday")
    old_done = create(api, "projects", name="Bench", status="done")
    age(old_active["id"], 30)
    age(older_paused["id"], 60)
    age(recent["id"], 20)
    age(old_someday["id"], 90)
    age(old_done["id"], 90)
    stale = api.get("/api/dashboard").json()["stale"]
    assert names(stale) == ["Shed", "Table saw"]  # oldest first
    assert stale[0]["status"] == "paused"


def test_threshold_comes_from_settings(api, age):
    project = create(api, "projects", name="Desk", status="active")
    age(project["id"], 10)
    assert api.get("/api/dashboard").json()["stale"] == []
    api.patch("/api/settings", json={"stale_after_days": 7})
    dashboard = api.get("/api/dashboard").json()
    assert names(dashboard["stale"]) == ["Desk"]
    assert dashboard["stale_after_days"] == 7


def test_touching_a_project_makes_it_fresh(api, age):
    project = create(api, "projects", name="Desk", status="active")
    age(project["id"], 30)
    api.post("/api/notes", json={"title": "Progress", "project_id": project["id"]})
    assert api.get("/api/dashboard").json()["stale"] == []
