import json
import os
import stat

import pytest
from fastapi.testclient import TestClient

from app.core.access import AccessMiddleware
from app.core.config import settings
from app.modules.mcp import token

LAN = ("192.168.1.50", 50000)  # e.g. Claude Code on a desktop, via the direct port
INGRESS = ("172.30.32.2", 50000)
HEADERS = {"accept": "application/json, text/event-stream", "content-type": "application/json"}


def rpc(method: str, params: dict | None = None) -> dict:
    return {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}


@pytest.fixture
def lan(api):
    """A client on the LAN, outside Ingress, with the MCP server running."""
    with TestClient(api.app, client=LAN) as client:
        yield client


@pytest.fixture
def mcp(lan):
    """Calls an MCP tool; returns its result, or raises with the error text."""
    auth = {**HEADERS, "authorization": f"Bearer {token.get_token()}"}

    def call(tool: str, /, **arguments):
        params = {"name": tool, "arguments": arguments}
        res = lan.post("/mcp", headers=auth, json=rpc("tools/call", params))
        assert res.status_code == 200, res.text
        result = res.json()["result"]
        text = result["content"][0]["text"] if result["content"] else ""
        if result.get("isError"):
            raise ToolError(text)
        if "structuredContent" in result:
            content = result["structuredContent"]
            # Non-object results (lists, strings) come wrapped as {"result": ...}.
            return content["result"] if set(content) == {"result"} else content
        return text

    call.lan = lan
    call.headers = auth
    return call


class ToolError(Exception):
    pass


# --- Access ---


@pytest.mark.parametrize("path", ["/", "/projects", "/api/health", "/api/mcp/token", "/api/docs"])
def test_lan_only_reaches_mcp(lan, path):
    res = lan.get(path)
    assert res.status_code == 403
    assert "Only /mcp" in res.json()["detail"]


def test_mcp_needs_the_token(lan):
    res = lan.post("/mcp", headers=HEADERS, json=rpc("tools/list"))
    assert res.status_code == 401
    assert res.headers["www-authenticate"] == "Bearer"
    for value in ("Bearer wrong", f"Basic {token.get_token()}", "Bearer ", token.get_token()):
        res = lan.post("/mcp", headers={**HEADERS, "authorization": value}, json=rpc("tools/list"))
        assert res.status_code == 401, value


def test_a_token_does_not_open_the_rest(lan):
    auth = {"authorization": f"Bearer {token.get_token()}"}
    assert lan.get("/api/health", headers=auth).status_code == 403


def test_forwarded_headers_are_not_trusted(lan):
    spoof = {"x-forwarded-for": "172.30.32.2", "x-real-ip": "127.0.0.1"}
    assert lan.get("/api/health", headers=spoof).status_code == 403


def test_ingress_reaches_everything(api):
    client = TestClient(api.app, client=INGRESS)
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/mcp/token").status_code == 200


def test_trusted_networks():
    middleware = AccessMiddleware(None, ["172.30.32.2", "10.0.0.0/8", "::1"], lambda t: False)
    assert middleware.is_trusted("172.30.32.2")
    assert middleware.is_trusted("10.1.2.3")
    assert middleware.is_trusted("::1")
    assert not middleware.is_trusted("172.30.32.1")
    assert not middleware.is_trusted("192.168.1.50")
    assert not middleware.is_trusted("testclient")


# --- Token ---


def test_token_is_kept_and_private(api):
    first = api.get("/api/mcp/token").json()["token"]
    assert len(first) >= 40
    assert api.get("/api/mcp/token").json()["token"] == first
    mode = stat.S_IMODE(os.stat(settings.data_dir / token.TOKEN_FILE).st_mode)
    assert mode == 0o600


def test_regenerating_retires_the_old_token(api, lan):
    old = api.get("/api/mcp/token").json()["token"]
    new = api.post("/api/mcp/token").json()["token"]
    assert new != old

    def status(value):
        auth = {**HEADERS, "authorization": f"Bearer {value}"}
        return lan.post("/mcp", headers=auth, json=rpc("tools/list")).status_code

    assert status(old) == 401
    assert status(new) == 200


# --- Tools ---


def test_tool_list(mcp):
    res = mcp.lan.post("/mcp", headers=mcp.headers, json=rpc("tools/list"))
    tools = {t["name"]: t for t in res.json()["result"]["tools"]}
    assert len(tools) == 24
    assert not [name for name in tools if "delete" in name or "remove" in name]
    assert tools["search"]["annotations"]["readOnlyHint"] is True
    assert tools["create_item"]["annotations"]["destructiveHint"] is False
    # Descriptions read as text, without code indentation.
    assert "\n    " not in tools["search"]["description"]


def test_records_skip_the_inbox_unless_asked(mcp, api):
    sorted_item = mcp("create_item", name="Wood glue", status="need")
    unsure = mcp("create_item", name="Thing from the shed", in_inbox=True)
    assert sorted_item["in_inbox"] is False
    inbox = mcp("get_inbox")
    assert [i["id"] for i in inbox["items"]] == [unsure["id"]]
    assert mcp("mark_sorted", record_type="item", record_id=unsure["id"]) == "Sorted item 2"
    assert api.get("/api/inbox/count").json() == {"count": 0}


def test_project_flow(mcp):
    project = mcp("create_project", name="Bird box", status="active", next_step="Cut the roof")
    glue = mcp("create_item", name="Wood glue", status="need")
    mcp("link_item_to_project", project_id=project["id"], item_id=glue["id"], note="small bottle")
    mcp("create_note", title="Plan", body_md="- [ ] measure", project_id=project["id"])
    mcp("add_link", owner_type="project", owner_id=project["id"], url="https://example.com/plans")

    context = mcp("get_project", project_id=project["id"])
    assert context["project"]["readiness"]["required"] == 1
    assert [link["item"]["name"] for link in context["items"]] == ["Wood glue"]
    assert [n["title"] for n in context["notes"]] == ["Plan"]
    assert [link["url"] for link in context["links"]] == ["https://example.com/plans"]

    updated = mcp("update_project", project_id=project["id"], next_step="Glue up")
    assert updated["next_step"] == "Glue up"
    assert updated["status"] == "active"  # untouched
    assert mcp("get_dashboard")["active"][0]["name"] == "Bird box"
    assert mcp("get_shopping_list")[0]["items"][0]["name"] == "Wood glue"

    mcp("unlink_item_from_project", project_id=project["id"], item_id=glue["id"])
    assert mcp("get_project", project_id=project["id"])["items"] == []


def test_update_item_changes_only_what_is_given(mcp):
    item = mcp("create_item", name="Saw", status="have", description="Old faithful")
    updated = mcp("update_item", item_id=item["id"], status="low")
    assert updated["status"] == "low"
    assert updated["name"] == "Saw"
    assert updated["description"] == "Old faithful"


def test_notes_can_only_grow(mcp):
    note = mcp("create_note", title="Ideas", body_md="# Shed\n\n- [ ] roof\n")
    appended = mcp("append_to_note", note_id=note["id"], text_md="- [ ] door")
    assert appended["body_md"] == "# Shed\n\n- [ ] roof\n\n- [ ] door\n"
    empty = mcp("create_note", title="Blank")
    assert mcp("append_to_note", note_id=empty["id"], text_md="First line")["body_md"] == (
        "First line\n"
    )
    renamed = mcp("update_note", note_id=note["id"], title="Shed ideas")
    assert renamed["title"] == "Shed ideas"
    assert renamed["body_md"] == appended["body_md"]


def test_search_reads_as_plain_text(mcp):
    mcp("create_item", name="Table saw blade")
    hits = mcp("search", query="saw")["items"]
    assert hits[0]["title"] == "Table saw blade"


def test_lookups(mcp, api):
    zone = api.post("/api/locations", json={"name": "Workshop"}).json()
    mcp("create_tag", name="Power tools")
    assert [loc["name"] for loc in mcp("list_locations")] == ["Workshop"]
    assert [tag["name"] for tag in mcp("list_tags")] == ["Power tools"]
    item = mcp("create_item", name="Drill", location_id=zone["id"])
    assert [i["id"] for i in mcp("list_items", location_id=zone["id"])] == [item["id"]]
    assert mcp("get_item", item_id=item["id"])["item"]["location_id"] == zone["id"]


def test_rules_still_apply(mcp):
    with pytest.raises(ToolError, match="http"):
        mcp("add_link", owner_type="item", owner_id=1, url="javascript:alert(1)")
    with pytest.raises(ToolError, match="not found"):
        mcp("get_project", project_id=999)
    with pytest.raises(ToolError):
        mcp("create_item", name="  ")


def test_results_are_json(mcp):
    # Structured results are also sent as JSON text, for clients that only read text.
    res = mcp.lan.post(
        "/mcp",
        headers=mcp.headers,
        json=rpc("tools/call", {"name": "get_dashboard", "arguments": {}}),
    )
    assert json.loads(res.json()["result"]["content"][0]["text"])["active"] == []
