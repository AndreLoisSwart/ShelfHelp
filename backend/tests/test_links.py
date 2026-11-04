import time

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.db import Base, create_db_engine, import_all_models
from app.modules.items.models import Item
from app.modules.links.models import Link
from app.modules.projects.models import Project


def make_owner(api, owner_type):
    path, body = {
        "project": ("/api/projects", {"name": "Shed"}),
        "item": ("/api/items", {"name": "Saw"}),
        "note": ("/api/notes", {"title": "Plan"}),
    }[owner_type]
    return api.post(path, json=body).json()["id"]


def links_of(api, owner_type, owner_id):
    return api.get(f"/api/links?owner_type={owner_type}&owner_id={owner_id}").json()


@pytest.mark.parametrize("owner_type", ["project", "item", "note"])
def test_crud_on_each_owner(api, owner_type):
    owner_id = make_owner(api, owner_type)
    res = api.post(
        "/api/links",
        json={
            "owner_type": owner_type,
            "owner_id": owner_id,
            "url": " https://example.com/manual.pdf ",
            "title": " Manual ",
        },
    )
    assert res.status_code == 201
    link = res.json()
    assert (link["url"], link["title"]) == ("https://example.com/manual.pdf", "Manual")
    assert links_of(api, owner_type, owner_id) == [link]

    updated = api.patch(f"/api/links/{link['id']}", json={"title": "Datasheet"}).json()
    assert updated["title"] == "Datasheet"
    assert api.delete(f"/api/links/{link['id']}").status_code == 204
    assert links_of(api, owner_type, owner_id) == []


@pytest.mark.parametrize(
    "url", ["javascript:alert(1)", "data:text/html,hi", "ftp://x.example", "example.com", "http://"]
)
def test_only_web_links_are_allowed(api, url):
    owner_id = make_owner(api, "project")
    body = {"owner_type": "project", "owner_id": owner_id, "url": url}
    assert api.post("/api/links", json=body).status_code == 422
    link = api.post("/api/links", json={**body, "url": "https://ok.example"}).json()
    assert api.patch(f"/api/links/{link['id']}", json={"url": url}).status_code == 422


def test_unknown_owner(api):
    body = {"owner_type": "item", "owner_id": 99, "url": "https://x.example"}
    assert api.post("/api/links", json=body).status_code == 404
    assert api.post("/api/links", json={**body, "owner_type": "shelf"}).status_code == 422
    assert api.get("/api/links?owner_type=note&owner_id=99").status_code == 404


def test_project_and_its_notes_links_touch_the_project(api):
    project_id = make_owner(api, "project")
    note_id = api.post("/api/notes", json={"title": "N", "project_id": project_id}).json()["id"]
    for owner_type, owner_id in (("project", project_id), ("note", note_id)):
        before = api.get(f"/api/projects/{project_id}").json()["last_touched_at"]
        time.sleep(0.01)
        body = {"owner_type": owner_type, "owner_id": owner_id, "url": "https://x.example"}
        api.post("/api/links", json=body)
        assert api.get(f"/api/projects/{project_id}").json()["last_touched_at"] > before


def test_deleting_owner_deletes_its_links(api):
    item_id = make_owner(api, "item")
    link = api.post(
        "/api/links", json={"owner_type": "item", "owner_id": item_id, "url": "https://x.example"}
    ).json()
    api.delete(f"/api/items/{item_id}")
    assert api.patch(f"/api/links/{link['id']}", json={"title": "x"}).status_code == 404


def test_database_requires_exactly_one_owner(tmp_path):
    engine = create_db_engine(f"sqlite:///{tmp_path / 'db.sqlite'}")
    import_all_models()
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        project = Project(name="P", status="someday")
        item = Item(name="I", status="have")
        session.add_all([project, item])
        session.flush()
        for owners in ({}, {"project_id": project.id, "item_id": item.id}):
            session.add(Link(url="https://x.example", **owners))
            with pytest.raises(IntegrityError):
                session.flush()
            session.rollback()
