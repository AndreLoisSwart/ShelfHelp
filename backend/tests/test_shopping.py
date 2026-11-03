def location(api, name, parent_id=None):
    return api.post("/api/locations", json={"name": name, "parent_id": parent_id}).json()["id"]


def item(api, name, **fields):
    return api.post("/api/items", json={"name": name, **fields}).json()


def summary(lists):
    return [
        (group["zone"]["name"] if group["zone"] else None, [i["name"] for i in group["items"]])
        for group in lists
    ]


def test_grouped_by_zone(api):
    workshop = location(api, "Workshop")
    shelf = location(api, "Shelf", workshop)
    box = location(api, "Box", shelf)
    home = location(api, "Home")
    location(api, "Garage")

    item(api, "screws", status="low", location_id=box)
    item(api, "Glue", status="out", location_id=workshop)
    item(api, "Saw", status="have", location_id=shelf)
    item(api, "Soap", status="need", location_id=home)
    item(api, "Batteries", status="need")

    assert summary(api.get("/api/shopping").json()) == [
        ("Garage", []),  # zones show even when empty
        ("Home", ["Soap"]),
        ("Workshop", ["Glue", "screws"]),  # a sub-sub-location counts towards its zone
        (None, ["Batteries"]),
    ]


def test_unassigned_only_when_needed(api):
    location(api, "Home")
    assert summary(api.get("/api/shopping").json()) == [("Home", [])]


def test_items_show_open_projects(api):
    blade = item(api, "Blade", status="need")
    for name, status in (("Shed", "active"), ("Boat", "planned"), ("Old desk", "done")):
        project = api.post("/api/projects", json={"name": name, "status": status}).json()
        api.put(f"/api/projects/{project['id']}/items/{blade['id']}", json={})
    entry = api.get("/api/shopping").json()[0]["items"][0]
    assert [p["name"] for p in entry["projects"]] == ["Boat", "Shed"]


def test_got_it_removes_from_list(api):
    soap = item(api, "Soap", status="need")
    api.patch(f"/api/items/{soap['id']}", json={"status": "have"})
    assert api.get("/api/shopping").json() == []
