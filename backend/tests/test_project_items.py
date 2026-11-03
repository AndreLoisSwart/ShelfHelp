import time


def project(api, name="Shed", **fields):
    return api.post("/api/projects", json={"name": name, **fields}).json()


def item(api, name, **fields):
    return api.post("/api/items", json={"name": name, **fields}).json()


def link(api, project_id, item_id, **body):
    return api.put(f"/api/projects/{project_id}/items/{item_id}", json=body)


def test_link_update_and_unlink(api):
    shed, saw = project(api), item(api, "Saw")
    res = link(api, shed["id"], saw["id"], note="  the big one  ")
    assert res.status_code == 200
    assert res.json()["requirement"] == "required"
    assert res.json()["note"] == "the big one"
    assert res.json()["item"]["name"] == "Saw"

    # Linking again updates the existing link rather than duplicating it.
    link(api, shed["id"], saw["id"], requirement="nice_to_have")
    links = api.get(f"/api/projects/{shed['id']}/items").json()
    assert [(link["item"]["id"], link["requirement"]) for link in links] == [
        (saw["id"], "nice_to_have")
    ]

    assert api.delete(f"/api/projects/{shed['id']}/items/{saw['id']}").status_code == 204
    assert api.get(f"/api/projects/{shed['id']}/items").json() == []
    assert api.delete(f"/api/projects/{shed['id']}/items/{saw['id']}").status_code == 404


def test_unknown_project_or_item_is_404(api):
    shed, saw = project(api), item(api, "Saw")
    assert link(api, 99, saw["id"]).status_code == 404
    assert link(api, shed["id"], 99).status_code == 404


def test_required_items_listed_first(api):
    shed = project(api)
    for name, requirement in (
        ("Axe", "nice_to_have"),
        ("Bolts", "required"),
        ("Clamp", "required"),
    ):
        link(api, shed["id"], item(api, name)["id"], requirement=requirement)
    names = [link["item"]["name"] for link in api.get(f"/api/projects/{shed['id']}/items").json()]
    assert names == ["Bolts", "Clamp", "Axe"]


def test_readiness(api):
    shed = project(api)
    for name, status, requirement in (
        ("Saw", "have", "required"),
        ("Glue", "low", "required"),
        ("Screws", "out", "required"),
        ("Hinges", "need", "required"),
        ("Paint", "have", "nice_to_have"),
        ("Varnish", "need", "nice_to_have"),
    ):
        link(api, shed["id"], item(api, name, status=status)["id"], requirement=requirement)
    expected = {"ready": 2, "required": 4, "nice_ready": 1, "nice_to_have": 2}
    assert api.get(f"/api/projects/{shed['id']}").json()["readiness"] == expected
    assert api.get("/api/projects").json()[0]["readiness"] == expected


def test_readiness_follows_item_status(api):
    shed, saw = project(api), item(api, "Saw", status="need")
    link(api, shed["id"], saw["id"])
    assert api.get(f"/api/projects/{shed['id']}").json()["readiness"]["ready"] == 0
    api.patch(f"/api/items/{saw['id']}", json={"status": "have"})
    assert api.get(f"/api/projects/{shed['id']}").json()["readiness"]["ready"] == 1


def test_project_without_links_has_zero_readiness(api):
    readiness = project(api)["readiness"]
    assert readiness == {"ready": 0, "required": 0, "nice_ready": 0, "nice_to_have": 0}


def test_link_changes_touch_project(api):
    shed, saw = project(api), item(api, "Saw")
    touched = shed["last_touched_at"]
    for change in (
        lambda: link(api, shed["id"], saw["id"]),
        lambda: link(api, shed["id"], saw["id"], note="new note"),
        lambda: api.delete(f"/api/projects/{shed['id']}/items/{saw['id']}"),
    ):
        time.sleep(0.01)
        change()
        now = api.get(f"/api/projects/{shed['id']}").json()["last_touched_at"]
        assert now > touched
        touched = now


def test_deleting_item_removes_link_and_touches_project(api):
    shed, saw = project(api), item(api, "Saw")
    link(api, shed["id"], saw["id"])
    before = api.get(f"/api/projects/{shed['id']}").json()["last_touched_at"]
    time.sleep(0.01)
    api.delete(f"/api/items/{saw['id']}")
    after = api.get(f"/api/projects/{shed['id']}").json()
    assert after["last_touched_at"] > before
    assert api.get(f"/api/projects/{shed['id']}/items").json() == []


def test_item_shows_projects_it_is_used_in(api):
    shed, boat, saw = project(api, "Shed"), project(api, "Boat"), item(api, "Saw")
    link(api, shed["id"], saw["id"], note="for the roof")
    link(api, boat["id"], saw["id"], requirement="nice_to_have")
    used_in = api.get(f"/api/items/{saw['id']}").json()["projects"]
    assert [(u["project"]["name"], u["requirement"], u["note"]) for u in used_in] == [
        ("Boat", "nice_to_have", ""),
        ("Shed", "required", "for the roof"),
    ]


def test_deleting_project_removes_links_not_items(api):
    shed, saw = project(api), item(api, "Saw")
    link(api, shed["id"], saw["id"])
    api.delete(f"/api/projects/{shed['id']}")
    assert api.get(f"/api/items/{saw['id']}").json()["projects"] == []
