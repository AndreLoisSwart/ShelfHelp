def test_crud_and_counts(api):
    tag = api.post("/api/tags", json={"name": "Wood"}).json()
    api.post("/api/items", json={"name": "Plank", "tag_ids": [tag["id"]]})
    assert api.get("/api/tags").json() == [{"id": tag["id"], "name": "Wood", "item_count": 1}]

    res = api.patch(f"/api/tags/{tag['id']}", json={"name": "Timber"})
    assert res.json()["name"] == "Timber"


def test_names_are_unique_ignoring_case(api):
    tag = api.post("/api/tags", json={"name": "Wood"}).json()
    res = api.post("/api/tags", json={"name": "wood"})
    assert res.status_code == 409
    assert res.json()["detail"] == 'A tag named "Wood" already exists'

    other = api.post("/api/tags", json={"name": "Metal"}).json()
    assert api.patch(f"/api/tags/{other['id']}", json={"name": "WOOD"}).status_code == 409
    # Changing only the case of its own name is fine.
    assert api.patch(f"/api/tags/{tag['id']}", json={"name": "wood"}).status_code == 200


def test_delete_removes_it_from_items(api):
    tag = api.post("/api/tags", json={"name": "Wood"}).json()
    item = api.post("/api/items", json={"name": "Plank", "tag_ids": [tag["id"]]}).json()
    assert api.delete(f"/api/tags/{tag['id']}").status_code == 204
    assert api.get(f"/api/items/{item['id']}").json()["tags"] == []
