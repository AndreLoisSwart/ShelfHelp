def test_defaults(api):
    assert api.get("/api/settings").json() == {"stale_after_days": 21}


def test_update(api):
    res = api.patch("/api/settings", json={"stale_after_days": 42})
    assert res.json() == {"stale_after_days": 42}
    assert api.get("/api/settings").json() == {"stale_after_days": 42}
    # Nothing sent, nothing changed.
    assert api.patch("/api/settings", json={}).json() == {"stale_after_days": 42}


def test_limits(api):
    for value in (6, 366, None, "soon"):
        res = api.patch("/api/settings", json={"stale_after_days": value})
        assert res.status_code == 422, value
