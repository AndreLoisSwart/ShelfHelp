from datetime import datetime


def make(api, name, **fields):
    res = api.post("/api/items", json={"name": name, **fields})
    assert res.status_code == 201, res.text
    return res.json()


def ids(items):
    return [item["id"] for item in items]


def test_create_defaults(api):
    item = make(api, "Table saw")
    assert item["status"] == "have"
    assert item["description"] == ""
    assert item["in_inbox"] is False
    assert item["parent"] is None and item["children"] == []
    assert datetime.fromisoformat(item["created_at"]).utcoffset().total_seconds() == 0


def test_invalid_status_is_rejected(api):
    assert api.post("/api/items", json={"name": "X", "status": "lost"}).status_code == 422


def test_unknown_references_are_404(api):
    for field in ("parent_id", "location_id"):
        assert api.post("/api/items", json={"name": "X", field: 99}).status_code == 404
    assert api.post("/api/items", json={"name": "X", "tag_ids": [99]}).status_code == 404


def test_parent_and_children(api):
    saw = make(api, "Table saw")
    blade = make(api, "Blade", parent_id=saw["id"])
    detail = api.get(f"/api/items/{saw['id']}").json()
    assert ids(detail["children"]) == [blade["id"]]
    parent = api.get(f"/api/items/{blade['id']}").json()["parent"]
    assert parent == {"id": saw["id"], "name": "Table saw"}


def test_parent_cycles_are_rejected(api):
    a = make(api, "A")
    b = make(api, "B", parent_id=a["id"])
    c = make(api, "C", parent_id=b["id"])
    for parent in (a, c):
        res = api.patch(f"/api/items/{a['id']}", json={"parent_id": parent["id"]})
        assert res.status_code == 409


def test_deleting_parent_makes_children_top_level(api):
    saw = make(api, "Table saw")
    blade = make(api, "Blade", parent_id=saw["id"])
    assert api.delete(f"/api/items/{saw['id']}").status_code == 204
    assert api.get(f"/api/items/{blade['id']}").json()["parent_id"] is None


def test_partial_update(api):
    loc = api.post("/api/locations", json={"name": "Shed"}).json()
    tag = api.post("/api/tags", json={"name": "Garden"}).json()
    item = make(api, "Hose", location_id=loc["id"], tag_ids=[tag["id"]])

    res = api.patch(f"/api/items/{item['id']}", json={"status": "low"}).json()
    assert res["status"] == "low"
    assert res["location_id"] == loc["id"]
    assert res["tags"] == [{"id": tag["id"], "name": "Garden"}]
    assert res["updated_at"] > item["updated_at"]

    res = api.patch(f"/api/items/{item['id']}", json={"location_id": None, "tag_ids": []}).json()
    assert res["location_id"] is None and res["tags"] == []


def test_non_clearable_fields_reject_null(api):
    item = make(api, "Hose")
    for field in ("name", "status", "description", "tag_ids", "in_inbox"):
        res = api.patch(f"/api/items/{item['id']}", json={field: None})
        assert res.status_code == 422, field


def test_filters(api):
    workshop = api.post("/api/locations", json={"name": "Workshop"}).json()["id"]
    shelf = api.post("/api/locations", json={"name": "Shelf", "parent_id": workshop}).json()["id"]
    home = api.post("/api/locations", json={"name": "Home"}).json()["id"]
    wood = api.post("/api/tags", json={"name": "Wood"}).json()["id"]

    glue = make(api, "glue", location_id=shelf, status="low", tag_ids=[wood])
    saw = make(api, "Saw", location_id=workshop)
    soap = make(api, "Soap", location_id=home, status="out")
    loose = make(api, "Loose", status="need")

    assert ids(api.get("/api/items").json()) == ids([glue, loose, saw, soap])  # case-insensitive
    # A location includes its sub-locations.
    assert ids(api.get(f"/api/items?location_id={workshop}").json()) == ids([glue, saw])
    assert ids(api.get(f"/api/items?location_id={shelf}").json()) == ids([glue])
    statuses = api.get("/api/items?status=low&status=out").json()
    assert ids(statuses) == ids([glue, soap])
    assert ids(api.get(f"/api/items?tag_id={wood}").json()) == ids([glue])
    combined = api.get(f"/api/items?location_id={workshop}&status=have").json()
    assert ids(combined) == ids([saw])
