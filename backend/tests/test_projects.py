import time


def make(api, name, **fields):
    res = api.post("/api/projects", json={"name": name, **fields})
    assert res.status_code == 201, res.text
    return res.json()


def ids(projects):
    return [project["id"] for project in projects]


def test_create_defaults(api):
    project = make(api, "Table saw restoration", next_step="  Order new belt  ")
    assert project["status"] == "someday"
    assert project["next_step"] == "Order new belt"
    assert project["description_md"] == ""
    assert project["in_inbox"] is False
    assert project["last_touched_at"] >= project["created_at"]


def test_invalid_status_and_long_next_step_are_rejected(api):
    assert api.post("/api/projects", json={"name": "X", "status": "busy"}).status_code == 422
    assert api.post("/api/projects", json={"name": "X", "next_step": "x" * 501}).status_code == 422


def test_update_touches_project(api):
    project = make(api, "Shed")
    time.sleep(0.01)
    res = api.patch(f"/api/projects/{project['id']}", json={"status": "active"}).json()
    assert res["status"] == "active"
    assert res["last_touched_at"] > project["last_touched_at"]
    assert res["updated_at"] > project["updated_at"]


def test_non_clearable_fields_reject_null(api):
    project = make(api, "Shed")
    for field in ("name", "status", "description_md", "next_step", "tag_ids", "in_inbox"):
        res = api.patch(f"/api/projects/{project['id']}", json={field: None})
        assert res.status_code == 422, field


def test_list_is_most_recently_touched_first(api):
    a, b, c = make(api, "A"), make(api, "B"), make(api, "C")
    assert ids(api.get("/api/projects").json()) == ids([c, b, a])
    api.patch(f"/api/projects/{a['id']}", json={"next_step": "Sand it"})
    assert ids(api.get("/api/projects").json()) == ids([a, c, b])


def test_filters(api):
    wood = api.post("/api/tags", json={"name": "Wood"}).json()["id"]
    shed = make(api, "Shed", status="active", tag_ids=[wood])
    boat = make(api, "Boat", status="paused")
    make(api, "Kite")
    assert ids(api.get("/api/projects?status=active&status=paused").json()) == ids([boat, shed])
    assert ids(api.get(f"/api/projects?tag_id={wood}").json()) == ids([shed])


def test_tags_count_and_cascade(api):
    wood = api.post("/api/tags", json={"name": "Wood"}).json()
    project = make(api, "Shed", tag_ids=[wood["id"]])
    api.post("/api/items", json={"name": "Plank", "tag_ids": [wood["id"]]})
    tag = api.get("/api/tags").json()[0]
    assert (tag["item_count"], tag["project_count"]) == (1, 1)

    api.delete(f"/api/tags/{wood['id']}")
    assert api.get(f"/api/projects/{project['id']}").json()["tags"] == []


def test_delete(api):
    project = make(api, "Shed")
    assert api.delete(f"/api/projects/{project['id']}").status_code == 204
    assert api.get(f"/api/projects/{project['id']}").status_code == 404
