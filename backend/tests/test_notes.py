import time

from app.modules.notes.service import excerpt


def project(api, name="Shed"):
    return api.post("/api/projects", json={"name": name}).json()


def note(api, title, **fields):
    res = api.post("/api/notes", json={"title": title, **fields})
    assert res.status_code == 201, res.text
    return res.json()


def touched(api, project_id):
    return api.get(f"/api/projects/{project_id}").json()["last_touched_at"]


def test_create_and_get(api):
    created = note(api, "  Ideas  ", body_md="# Plan\n\n- [ ] Buy **timber**\n")
    assert created["title"] == "Ideas"
    assert created["project"] is None
    fetched = api.get(f"/api/notes/{created['id']}").json()
    assert fetched["body_md"] == "# Plan\n\n- [ ] Buy **timber**\n"  # stored exactly as sent
    assert fetched["excerpt"] == "Plan Buy timber"


def test_unknown_project_is_404(api):
    assert api.post("/api/notes", json={"title": "X", "project_id": 99}).status_code == 404


def test_filters_and_order(api):
    shed = project(api)
    a = note(api, "A", project_id=shed["id"])
    b = note(api, "B")
    c = note(api, "C", project_id=shed["id"])
    ids = lambda res: [n["id"] for n in res.json()]  # noqa: E731
    assert ids(api.get("/api/notes")) == [c["id"], b["id"], a["id"]]
    assert ids(api.get(f"/api/notes?project_id={shed['id']}")) == [c["id"], a["id"]]
    assert ids(api.get("/api/notes?no_project=true")) == [b["id"]]
    time.sleep(0.01)
    api.patch(f"/api/notes/{a['id']}", json={"body_md": "edited"})
    assert ids(api.get("/api/notes"))[0] == a["id"]


def test_note_changes_touch_project(api):
    shed = project(api)

    def assert_touches(change):
        before = touched(api, shed["id"])
        time.sleep(0.01)
        result = change()
        assert touched(api, shed["id"]) > before
        return result

    n = assert_touches(lambda: note(api, "N", project_id=shed["id"]))
    assert_touches(lambda: api.patch(f"/api/notes/{n['id']}", json={"body_md": "more"}))
    assert_touches(lambda: api.delete(f"/api/notes/{n['id']}"))


def test_moving_a_note_touches_both_projects(api):
    shed, boat = project(api, "Shed"), project(api, "Boat")
    n = note(api, "N", project_id=shed["id"])
    before = touched(api, shed["id"]), touched(api, boat["id"])
    time.sleep(0.01)
    res = api.patch(f"/api/notes/{n['id']}", json={"project_id": boat["id"]}).json()
    assert res["project"]["name"] == "Boat"
    assert touched(api, shed["id"]) > before[0]
    assert touched(api, boat["id"]) > before[1]
    res = api.patch(f"/api/notes/{n['id']}", json={"project_id": None}).json()
    assert res["project"] is None


def test_deleting_project_keeps_its_notes(api):
    shed = project(api)
    n = note(api, "N", project_id=shed["id"])
    api.delete(f"/api/projects/{shed['id']}")
    assert api.get(f"/api/notes/{n['id']}").json()["project"] is None


def test_non_clearable_fields_reject_null(api):
    n = note(api, "N")
    for field in ("title", "body_md", "in_inbox"):
        assert api.patch(f"/api/notes/{n['id']}", json={field: None}).status_code == 422


def test_excerpt():
    assert excerpt("## Heading\n\n1. one\n2. two\n> quote") == "Heading one two quote"
    assert excerpt("- [x] done\n* [ ] todo") == "done todo"
    assert excerpt("See [the manual](http://x.y) and `code`") == "See the manual and code"
    long = excerpt("word " * 100)
    assert len(long) == 140 and long.endswith("…")
