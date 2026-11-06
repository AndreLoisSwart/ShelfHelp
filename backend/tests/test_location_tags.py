def tag(api, name):
    return api.post("/api/tags", json={"name": name}).json()["id"]


def location(api, name, parent_id=None, tag_ids=()):
    body = {"name": name, "parent_id": parent_id, "tag_ids": list(tag_ids)}
    return api.post("/api/locations", json=body).json()["id"]


def names(entity):
    return [t["name"] for t in entity["tags"]]


def test_items_get_their_location_and_ancestor_tags(api):
    garden, tools = tag(api, "Gardening"), tag(api, "Tools")
    shed = location(api, "Shed", tag_ids=[garden])
    shelf = location(api, "Shelf", shed, tag_ids=[tools])
    item = api.post("/api/items", json={"name": "Trowel", "location_id": shelf}).json()
    assert names(item) == ["Gardening", "Tools"]
    # Given tags are kept, without repeats.
    item = api.post(
        "/api/items", json={"name": "Hoe", "location_id": shed, "tag_ids": [garden]}
    ).json()
    assert names(item) == ["Gardening"]


def test_location_tags_are_copied_not_linked(api):
    garden = tag(api, "Gardening")
    shed = location(api, "Shed", tag_ids=[garden])
    item = api.post("/api/items", json={"name": "Trowel", "location_id": shed}).json()
    # The item can drop the tag, and editing other fields doesn't bring it back.
    api.patch(f"/api/items/{item['id']}", json={"tag_ids": []})
    item = api.patch(f"/api/items/{item['id']}", json={"status": "low", "location_id": shed})
    assert names(item.json()) == []
    # Removing it from the location leaves items alone.
    other = api.post("/api/items", json={"name": "Rake", "location_id": shed}).json()
    api.patch(f"/api/locations/{shed}", json={"tag_ids": []})
    assert names(api.get(f"/api/items/{other['id']}").json()) == ["Gardening"]
    assert api.get("/api/locations").json()[0]["tags"] == []


def test_moving_adds_but_never_removes(api):
    garden, power = tag(api, "Gardening"), tag(api, "Power tools")
    shed = location(api, "Shed", tag_ids=[garden])
    workshop = location(api, "Workshop", tag_ids=[power])
    item = api.post("/api/items", json={"name": "Drill", "location_id": shed}).json()
    item = api.patch(f"/api/items/{item['id']}", json={"location_id": workshop}).json()
    assert names(item) == ["Gardening", "Power tools"]
    # A tag list sent with the move is kept, plus the new location's tags.
    other = api.post("/api/items", json={"name": "Saw"}).json()
    other = api.patch(
        f"/api/items/{other['id']}", json={"location_id": shed, "tag_ids": [power]}
    ).json()
    assert names(other) == ["Gardening", "Power tools"]


def test_parts_get_their_parent_items_tags(api):
    power = tag(api, "Power tools")
    saw = api.post("/api/items", json={"name": "Table saw", "tag_ids": [power]}).json()
    blade = api.post("/api/items", json={"name": "Blade", "parent_id": saw["id"]}).json()
    assert names(blade) == ["Power tools"]
    loose = api.post("/api/items", json={"name": "Fence"}).json()
    moved = api.patch(f"/api/items/{loose['id']}", json={"parent_id": saw["id"]}).json()
    assert names(moved) == ["Power tools"]


def test_tagging_existing_items(api):
    garden = tag(api, "Gardening")
    shed = location(api, "Shed")
    shelf = location(api, "Shelf", shed)
    for name, where in (("Spade", shed), ("Gloves", shelf), ("Elsewhere", None)):
        api.post("/api/items", json={"name": name, "location_id": where})
    api.post("/api/items", json={"name": "Hoe", "location_id": shed, "tag_ids": [garden]})

    url = f"/api/locations/{shed}/tag-items/{garden}"
    assert api.get(url).json() == {"count": 2}  # includes sub-locations, skips the Hoe
    assert api.post(url).json() == {"count": 2}
    assert api.get(url).json() == {"count": 0}
    assert api.get(f"/api/locations/{shed}/tag-items/999").status_code == 404


def test_deleting_a_tag_or_location_clears_links(api):
    garden = tag(api, "Gardening")
    shed = location(api, "Shed", tag_ids=[garden])
    api.delete(f"/api/tags/{garden}")
    assert api.get("/api/locations").json()[0]["tags"] == []
    assert api.delete(f"/api/locations/{shed}").status_code == 204


def test_projects_suggest_their_items_tags(api):
    wood, glue, outdoor = tag(api, "Wood"), tag(api, "Glue"), tag(api, "Outdoor")
    project = api.post("/api/projects", json={"name": "Bird box", "tag_ids": [outdoor]}).json()
    for name, tags in (("Plank", [wood, outdoor]), ("Offcut", [wood]), ("Wood glue", [glue])):
        item = api.post("/api/items", json={"name": name, "tag_ids": tags}).json()
        api.put(f"/api/projects/{project['id']}/items/{item['id']}", json={})
    detail = api.get(f"/api/projects/{project['id']}").json()
    # Most used first; never ones the project has; never added by themselves.
    assert [t["name"] for t in detail["suggested_tags"]] == ["Wood", "Glue"]
    assert names(detail) == ["Outdoor"]
