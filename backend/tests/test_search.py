from app.modules.search.service import match_query

S, E = "\x02", "\x03"


def create(api, kind, **fields):
    res = api.post(f"/api/{kind}", json=fields)
    assert res.status_code == 201, res.text
    return res.json()


def search(api, q):
    res = api.get("/api/search", params={"q": q})
    assert res.status_code == 200, res.text
    return res.json()


def ids(hits):
    return [hit["id"] for hit in hits]


def test_finds_each_kind_by_prefix(api):
    project = create(api, "projects", name="Table saw restoration", next_step="Order belts")
    item = create(api, "items", name="Saw blade", description="80 tooth, for the table saw")
    note = create(api, "notes", title="Fence ideas", body_md="# Saw fence\n\n- [ ] **measure**")
    results = search(api, "sa")
    assert ids(results["projects"]) == [project["id"]]
    assert ids(results["items"]) == [item["id"]]
    assert ids(results["notes"]) == [note["id"]]
    assert results["projects"][0]["status"] == "someday"
    assert results["items"][0]["status"] == "have"
    assert results["items"][0]["title"] == f"{S}Saw{E} blade"
    # Note bodies come back as plain text, with the match marked.
    assert results["notes"][0]["snippet"] == f"{S}Saw{E} fence measure"


def test_every_word_must_match_case_and_accents_ignored(api):
    create(api, "items", name="Café table")
    create(api, "items", name="Coffee grinder")
    assert len(search(api, "CAFE tab")["items"]) == 1
    assert search(api, "cafe grinder")["items"] == []


def test_searches_next_step_and_description(api):
    project = create(api, "projects", name="Shed", next_step="Buy hinges")
    create(api, "projects", name="Desk", description_md="Oak top, **hinged** flap")
    assert ids(search(api, "hinges")["projects"]) == [project["id"]]
    assert len(search(api, "hinge")["projects"]) == 2


def test_title_matches_rank_first(api):
    in_body = create(api, "notes", title="Plans", body_md="Router table, router bits")
    in_title = create(api, "notes", title="Router", body_md="")
    assert ids(search(api, "router")["notes"]) == [in_title["id"], in_body["id"]]


def test_index_follows_updates_and_deletes(api):
    item = create(api, "items", name="Drill")
    api.patch(f"/api/items/{item['id']}", json={"name": "Impact driver"})
    assert search(api, "drill")["items"] == []
    assert ids(search(api, "impact")["items"]) == [item["id"]]
    # Other changes keep it findable.
    api.patch(f"/api/items/{item['id']}", json={"status": "need"})
    assert ids(search(api, "impact")["items"]) == [item["id"]]
    api.delete(f"/api/items/{item['id']}")
    assert search(api, "impact")["items"] == []

    note = create(api, "notes", title="Draft", body_md="old words")
    api.patch(f"/api/notes/{note['id']}", json={"body_md": "new words"})
    assert search(api, "old")["notes"] == []
    assert ids(search(api, "new")["notes"]) == [note["id"]]


def test_at_most_five_of_each(api):
    for n in range(7):
        create(api, "items", name=f"Screw {n}")
    assert len(search(api, "screw")["items"]) == 5


def test_query_syntax_is_inert(api):
    create(api, "items", name="Bolt")
    for q in ['"', "bolt OR", "NOT bolt", "bolt*", "(bolt", "title:bolt", "-bolt", "^bolt"]:
        res = api.get("/api/search", params={"q": q})
        assert res.status_code == 200, q
    assert len(search(api, "NOT bolt")["items"]) == 0  # "not" is just a word to match
    assert len(search(api, "bolt*")["items"]) == 1


def test_empty_and_overlong_queries(api):
    create(api, "items", name="Bolt")
    assert search(api, "  ?! ") == {"projects": [], "items": [], "notes": []}
    assert search(api, "") == {"projects": [], "items": [], "notes": []}
    assert api.get("/api/search", params={"q": "x" * 201}).status_code == 422


def test_match_query():
    assert match_query('tab "saw" OR') == '"tab"* "saw"* "OR"*'
    assert match_query("--") is None
