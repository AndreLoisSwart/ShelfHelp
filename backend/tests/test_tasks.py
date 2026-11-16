import time


def make_project(api, name="Shed", **fields):
    res = api.post("/api/projects", json={"name": name, **fields})
    assert res.status_code == 201, res.text
    return res.json()


def make(api, title, **fields):
    res = api.post("/api/tasks", json={"title": title, **fields})
    assert res.status_code == 201, res.text
    return res.json()


def titles(tasks):
    return [task["title"] for task in tasks]


def project(api, project_id):
    return api.get(f"/api/projects/{project_id}").json()


def test_standalone_defaults(api):
    task = make(api, "  Fix the gate  ", description="  hinge is loose ")
    assert task["title"] == "Fix the gate"
    assert task["description"] == "hinge is loose"
    assert task["project"] is None
    assert task["done_at"] is None
    assert task["in_inbox"] is False
    assert task["readiness"] == {"ready": 0, "total": 0}


def test_validation(api):
    assert api.post("/api/tasks", json={"title": " "}).status_code == 422
    assert api.post("/api/tasks", json={"title": "x" * 201}).status_code == 422
    assert api.post("/api/tasks", json={"title": "X", "project_id": 99}).status_code == 404
    assert api.post("/api/tasks", json={"title": "X", "item_ids": [99]}).status_code == 404
    task = make(api, "X")
    for field in ("title", "description", "tag_ids", "item_ids", "done", "in_inbox"):
        assert api.patch(f"/api/tasks/{task['id']}", json={field: None}).status_code == 422


def test_first_open_task_is_the_next_step(api):
    shed = make_project(api)
    first = make(api, "Pour base", project_id=shed["id"])
    make(api, "Build frame", project_id=shed["id"])
    assert project(api, shed["id"])["next_task"] == {"id": first["id"], "title": "Pour base"}

    api.patch(f"/api/tasks/{first['id']}", json={"done": True})
    detail = project(api, shed["id"])
    assert detail["next_task"]["title"] == "Build frame"
    assert detail["task_counts"] == {"open": 1, "done": 1}

    api.patch(f"/api/tasks/{first['id']}", json={"done": False})
    assert project(api, shed["id"])["next_task"]["title"] == "Pour base"


def test_list_order_open_then_recently_done(api):
    shed = make_project(api)
    a, b, c, d = (make(api, t, project_id=shed["id"]) for t in "ABCD")
    api.patch(f"/api/tasks/{b['id']}", json={"done": True})
    time.sleep(0.01)
    api.patch(f"/api/tasks/{d['id']}", json={"done": True})
    listed = api.get(f"/api/tasks?project_id={shed['id']}").json()
    assert titles(listed) == ["A", "C", "D", "B"]
    assert titles(api.get("/api/tasks?done=false").json()) == ["A", "C"]
    assert titles(api.get("/api/tasks?done=true").json()) == ["D", "B"]


def test_ticking_twice_keeps_the_done_time(api):
    task = make(api, "X")
    done = api.patch(f"/api/tasks/{task['id']}", json={"done": True}).json()["done_at"]
    assert api.patch(f"/api/tasks/{task['id']}", json={"done": True}).json()["done_at"] == done


def test_filters(api):
    shed = make_project(api)
    wood = api.post("/api/tags", json={"name": "Wood"}).json()["id"]
    make(api, "In shed", project_id=shed["id"])
    make(api, "Loose", tag_ids=[wood])
    assert titles(api.get("/api/tasks?no_project=true").json()) == ["Loose"]
    assert titles(api.get(f"/api/tasks?project_id={shed['id']}").json()) == ["In shed"]
    assert titles(api.get(f"/api/tasks?tag_id={wood}").json()) == ["Loose"]


def test_reorder(api):
    shed = make_project(api)
    a, b, c = (make(api, t, project_id=shed["id"])["id"] for t in "ABC")
    res = api.put("/api/tasks/order", json={"project_id": shed["id"], "task_ids": [c]})
    assert titles(res.json()) == ["C", "A", "B"]
    assert project(api, shed["id"])["next_task"]["id"] == c

    res = api.put("/api/tasks/order", json={"project_id": shed["id"], "task_ids": [b, a, c]})
    assert titles(res.json()) == ["B", "A", "C"]

    # A done task, or one from elsewhere, can't be ordered here.
    loose = make(api, "Loose")["id"]
    api.patch(f"/api/tasks/{a}", json={"done": True})
    for wrong in (a, loose):
        res = api.put("/api/tasks/order", json={"project_id": shed["id"], "task_ids": [wrong]})
        assert res.status_code == 409

    # Standalone tasks have their own order.
    other = make(api, "Other")["id"]
    res = api.put("/api/tasks/order", json={"project_id": None, "task_ids": [other]})
    assert titles(res.json()) == ["Other", "Loose"]


def test_new_and_moved_tasks_go_to_the_bottom_with_project_tags(api):
    wood = api.post("/api/tags", json={"name": "Wood"}).json()["id"]
    paint = api.post("/api/tags", json={"name": "Paint"}).json()["id"]
    shed = make_project(api, tag_ids=[wood])
    make(api, "First", project_id=shed["id"])
    task = make(api, "Loose", tag_ids=[paint])
    assert [t["name"] for t in task["tags"]] == ["Paint"]

    moved = api.patch(f"/api/tasks/{task['id']}", json={"project_id": shed["id"]}).json()
    assert [t["name"] for t in moved["tags"]] == ["Paint", "Wood"]
    listed = api.get(f"/api/tasks?project_id={shed['id']}").json()
    assert titles(listed) == ["First", "Loose"]

    # Back out of the project: the tags stay, as they're only ever added.
    back = api.patch(f"/api/tasks/{task['id']}", json={"project_id": None}).json()
    assert back["project"] is None
    assert len(back["tags"]) == 2


def test_task_changes_touch_projects(api):
    shed, boat = make_project(api, "Shed"), make_project(api, "Boat")

    def touched(p):
        return project(api, p["id"])["last_touched_at"]

    before = touched(shed)
    time.sleep(0.01)
    task = make(api, "X", project_id=shed["id"])
    assert touched(shed) > before

    before_shed, before_boat = touched(shed), touched(boat)
    time.sleep(0.01)
    api.patch(f"/api/tasks/{task['id']}", json={"project_id": boat["id"]})
    assert touched(shed) > before_shed
    assert touched(boat) > before_boat

    before = touched(boat)
    time.sleep(0.01)
    api.delete(f"/api/tasks/{task['id']}")
    assert touched(boat) > before


def test_linked_items_and_readiness(api):
    saw = api.post("/api/items", json={"name": "Saw"}).json()
    glue = api.post("/api/items", json={"name": "Glue", "status": "need"}).json()
    task = make(api, "Cut and glue", item_ids=[saw["id"], glue["id"], saw["id"]])
    assert [i["name"] for i in task["items"]] == ["Glue", "Saw"]
    assert task["readiness"] == {"ready": 1, "total": 2}

    api.delete(f"/api/items/{glue['id']}")
    detail = api.get(f"/api/tasks/{task['id']}").json()
    assert detail["readiness"] == {"ready": 1, "total": 1}

    cleared = api.patch(f"/api/tasks/{task['id']}", json={"item_ids": []}).json()
    assert cleared["items"] == []
    assert api.get(f"/api/items/{saw['id']}").status_code == 200


def test_deleting_a_project_deletes_its_tasks(api):
    shed = make_project(api)
    task = make(api, "X", project_id=shed["id"])
    api.delete(f"/api/projects/{shed['id']}")
    assert api.get(f"/api/tasks/{task['id']}").status_code == 404


def test_tags_count_and_cascade(api):
    wood = api.post("/api/tags", json={"name": "Wood"}).json()
    task = make(api, "X", tag_ids=[wood["id"]])
    assert api.get("/api/tags").json()[0]["task_count"] == 1
    api.delete(f"/api/tags/{wood['id']}")
    assert api.get(f"/api/tasks/{task['id']}").json()["tags"] == []


def test_inbox(api):
    task = make(api, "Sort me", in_inbox=True)
    inbox = api.get("/api/inbox").json()
    assert [t["id"] for t in inbox["tasks"]] == [task["id"]]
    assert api.get("/api/inbox/count").json() == {"count": 1}
    api.patch(f"/api/tasks/{task['id']}", json={"in_inbox": False})
    assert api.get("/api/inbox/count").json() == {"count": 0}
