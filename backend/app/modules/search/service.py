import re

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.markdown import plain_text
from app.modules.search.index import TABLE
from app.modules.search.schemas import ItemHit, ProjectHit, SearchHit, SearchResults

LIMIT = 5
MARK_START, MARK_END = "\x02", "\x03"
SNIPPET_WORDS = 12


def match_query(q: str) -> str | None:
    """Every word must match, each as a prefix: "tab sa" finds "Table saw".

    Words are quoted, so nothing typed can use FTS5 query syntax."""
    words = re.findall(r"\w+", q)
    return " ".join(f'"{word}"*' for word in words) or None


def _hits(session: Session, kind: str, table: str, match: str, with_status: bool) -> list[dict]:
    status = f", {table}.status" if with_status else ""
    rows = session.execute(
        text(
            f"SELECT {TABLE}.record_id, "
            f"highlight({TABLE}, 2, :start, :end), "
            f"snippet({TABLE}, 3, :start, :end, '…', {SNIPPET_WORDS}){status} "
            f"FROM {TABLE} JOIN {table} ON {table}.id = {TABLE}.record_id "
            f"WHERE {TABLE} MATCH :match AND {TABLE}.kind = :kind "
            # A match in the title counts ten times one in the body.
            f"ORDER BY bm25({TABLE}, 0, 0, 10.0, 1.0) LIMIT {LIMIT}"
        ),
        {"start": MARK_START, "end": MARK_END, "match": match, "kind": kind},
    )
    hits = []
    for row in rows:
        hit = {"id": row[0], "title": row[1], "snippet": plain_text(row[2])}
        if with_status:
            hit["status"] = row[3]
        hits.append(hit)
    return hits


def search(session: Session, q: str) -> SearchResults:
    match = match_query(q)
    if match is None:
        return SearchResults(projects=[], items=[], notes=[])
    return SearchResults(
        projects=[ProjectHit(**h) for h in _hits(session, "project", "projects", match, True)],
        items=[ItemHit(**h) for h in _hits(session, "item", "items", match, True)],
        notes=[SearchHit(**h) for h in _hits(session, "note", "notes", match, False)],
    )
