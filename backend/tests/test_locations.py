def make(api, name, parent_id=None):
    res = api.post("/api/locations", json={"name": name, "parent_id": parent_id})
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_create_and_list_tree(api):
    workshop = make(api, "Workshop")
    shelf = make(api, "  Shelf A  ", workshop)
    locations = {loc["id"]: loc for loc in api.get("/api/locations").json()}
    expected = {"id": shelf, "name": "Shelf A", "parent_id": workshop, "item_count": 0, "tags": []}
    assert locations[shelf] == expected


def test_blank_name_is_rejected(api):
    assert api.post("/api/locations", json={"name": "   "}).status_code == 422


def test_unknown_parent_is_404(api):
    assert api.post("/api/locations", json={"name": "X", "parent_id": 99}).status_code == 404


def test_rename_and_move(api):
    home, workshop = make(api, "Home"), make(api, "Workshop")
    shelf = make(api, "Shelf", home)
    res = api.patch(f"/api/locations/{shelf}", json={"name": "Rack", "parent_id": workshop})
    assert res.json()["name"] == "Rack" and res.json()["parent_id"] == workshop
    res = api.patch(f"/api/locations/{shelf}", json={"parent_id": None})
    assert res.json()["parent_id"] is None


def test_null_name_is_rejected(api):
    loc = make(api, "Home")
    assert api.patch(f"/api/locations/{loc}", json={"name": None}).status_code == 422


def test_cannot_move_inside_itself(api):
    top = make(api, "Workshop")
    mid = make(api, "Shelf", top)
    low = make(api, "Box", mid)
    for target in (top, low):
        res = api.patch(f"/api/locations/{top}", json={"parent_id": target})
        assert res.status_code == 409


def test_delete_blocked_by_children_and_items(api):
    top = make(api, "Workshop")
    shelf = make(api, "Shelf", top)
    assert api.delete(f"/api/locations/{top}").status_code == 409

    item = api.post("/api/items", json={"name": "Saw", "location_id": shelf}).json()
    res = api.delete(f"/api/locations/{shelf}")
    assert res.status_code == 409
    assert "1 item is stored here" in res.json()["detail"]

    api.delete(f"/api/items/{item['id']}")
    assert api.delete(f"/api/locations/{shelf}").status_code == 204
    assert api.delete(f"/api/locations/{top}").status_code == 204
    assert api.get("/api/locations").json() == []
