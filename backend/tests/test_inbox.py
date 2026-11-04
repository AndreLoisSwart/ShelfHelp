def create(api, kind, **fields):
    res = api.post(f"/api/{kind}", json=fields)
    assert res.status_code == 201, res.text
    return res.json()


def test_quick_added_records_land_in_the_inbox(api):
    create(api, "items", name="Not captured")
    first = create(api, "items", name="Glue", status="need", in_inbox=True)
    second = create(api, "items", name="Clamps", in_inbox=True)
    project = create(api, "projects", name="Bird box", in_inbox=True)
    note = create(api, "notes", title="Idea", body_md="**Big** idea", in_inbox=True)

    inbox = api.get("/api/inbox").json()
    assert [i["id"] for i in inbox["items"]] == [second["id"], first["id"]]  # newest first
    assert [p["id"] for p in inbox["projects"]] == [project["id"]]
    assert inbox["projects"][0]["readiness"]["required"] == 0
    assert [n["id"] for n in inbox["notes"]] == [note["id"]]
    assert inbox["notes"][0]["excerpt"] == "Big idea"
    assert api.get("/api/inbox/count").json() == {"count": 4}


def test_records_default_to_outside_the_inbox(api):
    item = create(api, "items", name="Glue")
    assert item["in_inbox"] is False
    assert api.get("/api/inbox/count").json() == {"count": 0}


def test_inbox_records_count_everywhere_else(api):
    create(api, "items", name="Glue", status="need", in_inbox=True)
    shopping = api.get("/api/shopping").json()
    assert [i["name"] for zone in shopping for i in zone["items"]] == ["Glue"]
    assert len(api.get("/api/search", params={"q": "glue"}).json()["items"]) == 1


def test_done_clears_the_flag(api):
    item = create(api, "items", name="Glue", in_inbox=True)
    note = create(api, "notes", title="Idea", in_inbox=True)
    api.patch(f"/api/items/{item['id']}", json={"in_inbox": False})
    api.patch(f"/api/notes/{note['id']}", json={"in_inbox": False})
    assert api.get("/api/inbox").json() == {"items": [], "projects": [], "notes": []}
    assert api.get("/api/inbox/count").json() == {"count": 0}


def test_sorting_fields_keep_it_in_the_inbox(api):
    """Only Done clears the flag; filling in details doesn't."""
    project = create(api, "projects", name="Bird box", in_inbox=True)
    api.patch(f"/api/projects/{project['id']}", json={"status": "planned"})
    assert api.get("/api/inbox/count").json() == {"count": 1}
