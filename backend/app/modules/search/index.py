"""The full-text search index: one FTS5 table over projects, items and notes.

SQLite triggers keep it in sync, so no code path can forget to update it. The SQL is
frozen into the migration that creates it, and tests/test_db.py checks the migrated
database ends up with exactly this schema.

Careful: SQLite drops a table's triggers with the table, and Alembic batch migrations
rebuild tables. A migration that rebuilds projects, items or notes must recreate their
triggers (test_db.py fails if it doesn't).
"""

from dataclasses import dataclass

TABLE = "search_index"


@dataclass(frozen=True)
class Source:
    kind: str
    table: str
    title: str
    body: str  # an SQL expression, with {r} standing for the row
    columns: tuple[str, ...]  # changes to these re-index the row


SOURCES = (
    Source(
        "project",
        "projects",
        "name",
        "{r}.next_step || char(10) || {r}.description_md",
        ("name", "next_step", "description_md"),
    ),
    Source("item", "items", "name", "{r}.description", ("name", "description")),
    Source("note", "notes", "title", "{r}.body_md", ("title", "body_md")),
)


def _row(source: Source, ref: str) -> str:
    return (
        f"INSERT INTO {TABLE} (kind, record_id, title, body) "
        f"VALUES ('{source.kind}', {ref}.id, {ref}.{source.title}, {source.body.format(r=ref)});"
    )


def _remove(source: Source) -> str:
    return f"DELETE FROM {TABLE} WHERE kind = '{source.kind}' AND record_id = old.id;"


def create_statements() -> list[str]:
    statements = [
        # kind and record_id are stored, not searched. unicode61 folds case and, with
        # remove_diacritics, accents: "Cafe" finds "Café".
        f"CREATE VIRTUAL TABLE {TABLE} USING fts5("
        "kind UNINDEXED, record_id UNINDEXED, title, body, "
        "tokenize = 'unicode61 remove_diacritics 2')"
    ]
    for s in SOURCES:
        statements += [
            f"CREATE TRIGGER {TABLE}_{s.table}_insert AFTER INSERT ON {s.table} "
            f"BEGIN {_row(s, 'new')} END",
            f"CREATE TRIGGER {TABLE}_{s.table}_update "
            f"AFTER UPDATE OF {', '.join(s.columns)} ON {s.table} "
            f"BEGIN {_remove(s)} {_row(s, 'new')} END",
            f"CREATE TRIGGER {TABLE}_{s.table}_delete AFTER DELETE ON {s.table} "
            f"BEGIN {_remove(s)} END",
        ]
    return statements


def is_search_table(name: str | None) -> bool:
    """The FTS table and its shadow tables, which Alembic must not try to manage."""
    return name is not None and (name == TABLE or name.startswith(f"{TABLE}_"))
