def shop(api, name):
    return api.post("/api/shops", json={"name": name}).json()


def test_crud_and_counts(api):
    builders = shop(api, "Builders")
    api.post("/api/items", json={"name": "Screws", "shop_ids": [builders["id"]]})
    assert api.get("/api/shops").json() == [
        {"id": builders["id"], "name": "Builders", "item_count": 1}
    ]

    res = api.patch(f"/api/shops/{builders['id']}", json={"name": "Builders Warehouse"})
    assert res.json()["name"] == "Builders Warehouse"


def test_names_are_unique_ignoring_case(api):
    shop(api, "Makro")
    res = api.post("/api/shops", json={"name": "makro"})
    assert res.status_code == 409
    assert res.json()["detail"] == 'A shop named "Makro" already exists'


def test_items_keep_several_shops(api):
    makro, builders = shop(api, "Makro"), shop(api, "Builders")
    item = api.post(
        "/api/items", json={"name": "Glue", "shop_ids": [makro["id"], builders["id"], makro["id"]]}
    ).json()
    assert [s["name"] for s in item["shops"]] == ["Builders", "Makro"]  # by name, no repeats

    # Other fields leave shops alone; shop_ids replaces them.
    item = api.patch(f"/api/items/{item['id']}", json={"status": "low"}).json()
    assert len(item["shops"]) == 2
    item = api.patch(f"/api/items/{item['id']}", json={"shop_ids": [makro["id"]]}).json()
    assert [s["name"] for s in item["shops"]] == ["Makro"]

    assert api.post("/api/items", json={"name": "X", "shop_ids": [999]}).status_code == 404
    assert api.patch(f"/api/items/{item['id']}", json={"shop_ids": None}).status_code == 422


def test_delete_removes_it_from_items(api):
    makro = shop(api, "Makro")
    item = api.post("/api/items", json={"name": "Glue", "shop_ids": [makro["id"]]}).json()
    assert api.delete(f"/api/shops/{makro['id']}").status_code == 204
    assert api.get(f"/api/items/{item['id']}").json()["shops"] == []


def test_shopping_list_by_shop(api):
    makro, builders = shop(api, "Makro"), shop(api, "Builders")
    home = api.post("/api/locations", json={"name": "Home"}).json()["id"]
    workshop = api.post("/api/locations", json={"name": "Workshop"}).json()["id"]

    def need(name, location_id, *shops):
        shop_ids = [s["id"] for s in shops]
        body = {"name": name, "status": "need", "location_id": location_id, "shop_ids": shop_ids}
        api.post("/api/items", json=body)

    need("Bulbs", home, builders, makro)
    need("Coffee", home, makro)
    need("Screws", workshop, builders)
    need("Sandpaper", workshop)  # no shop set
    api.post("/api/items", json={"name": "Saw", "status": "have", "shop_ids": [builders["id"]]})

    def names(**params):
        lists = api.get("/api/shopping", params=params).json()
        return {group["zone"]["name"]: [i["name"] for i in group["items"]] for group in lists}

    # Across zones; items with no shop stay on the list.
    assert names(shop_id=builders["id"]) == {"Home": ["Bulbs"], "Workshop": ["Sandpaper", "Screws"]}
    assert names(shop_id=makro["id"]) == {"Home": ["Bulbs", "Coffee"], "Workshop": ["Sandpaper"]}
    assert names() == {"Home": ["Bulbs", "Coffee"], "Workshop": ["Sandpaper", "Screws"]}
    assert api.get("/api/shopping", params={"shop_id": 999}).status_code == 404
