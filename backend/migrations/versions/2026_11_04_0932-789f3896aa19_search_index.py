"""search index

Revision ID: 789f3896aa19
Revises: 144cf2e97f53
Create Date: 2026-11-04 09:32:14.027939

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "789f3896aa19"
down_revision: str | Sequence[str] | None = "144cf2e97f53"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# ruff: noqa: E501 (frozen SQL, kept on one line per statement)

# The SQL as it was when this migration was written; app/modules/search/index.py
# generates the current version, and tests/test_db.py checks the two agree.
STATEMENTS = [
    "CREATE VIRTUAL TABLE search_index USING fts5(kind UNINDEXED, record_id UNINDEXED, title, body, tokenize = 'unicode61 remove_diacritics 2')",
    "CREATE TRIGGER search_index_projects_insert AFTER INSERT ON projects BEGIN INSERT INTO search_index (kind, record_id, title, body) VALUES ('project', new.id, new.name, new.next_step || char(10) || new.description_md); END",
    "CREATE TRIGGER search_index_projects_update AFTER UPDATE OF name, next_step, description_md ON projects BEGIN DELETE FROM search_index WHERE kind = 'project' AND record_id = old.id; INSERT INTO search_index (kind, record_id, title, body) VALUES ('project', new.id, new.name, new.next_step || char(10) || new.description_md); END",
    "CREATE TRIGGER search_index_projects_delete AFTER DELETE ON projects BEGIN DELETE FROM search_index WHERE kind = 'project' AND record_id = old.id; END",
    "CREATE TRIGGER search_index_items_insert AFTER INSERT ON items BEGIN INSERT INTO search_index (kind, record_id, title, body) VALUES ('item', new.id, new.name, new.description); END",
    "CREATE TRIGGER search_index_items_update AFTER UPDATE OF name, description ON items BEGIN DELETE FROM search_index WHERE kind = 'item' AND record_id = old.id; INSERT INTO search_index (kind, record_id, title, body) VALUES ('item', new.id, new.name, new.description); END",
    "CREATE TRIGGER search_index_items_delete AFTER DELETE ON items BEGIN DELETE FROM search_index WHERE kind = 'item' AND record_id = old.id; END",
    "CREATE TRIGGER search_index_notes_insert AFTER INSERT ON notes BEGIN INSERT INTO search_index (kind, record_id, title, body) VALUES ('note', new.id, new.title, new.body_md); END",
    "CREATE TRIGGER search_index_notes_update AFTER UPDATE OF title, body_md ON notes BEGIN DELETE FROM search_index WHERE kind = 'note' AND record_id = old.id; INSERT INTO search_index (kind, record_id, title, body) VALUES ('note', new.id, new.title, new.body_md); END",
    "CREATE TRIGGER search_index_notes_delete AFTER DELETE ON notes BEGIN DELETE FROM search_index WHERE kind = 'note' AND record_id = old.id; END",
]

TRIGGERS = [
    f"search_index_{table}_{event}"
    for table in ("projects", "items", "notes")
    for event in ("insert", "update", "delete")
]


def upgrade() -> None:
    """Upgrade schema."""
    for statement in STATEMENTS:
        op.execute(statement)
    # Index what's already there.
    op.execute(
        "INSERT INTO search_index (kind, record_id, title, body) "
        "SELECT 'project', id, name, next_step || char(10) || description_md FROM projects"
    )
    op.execute(
        "INSERT INTO search_index (kind, record_id, title, body) "
        "SELECT 'item', id, name, description FROM items"
    )
    op.execute(
        "INSERT INTO search_index (kind, record_id, title, body) "
        "SELECT 'note', id, title, body_md FROM notes"
    )


def downgrade() -> None:
    """Downgrade schema."""
    for trigger in TRIGGERS:
        op.execute(f"DROP TRIGGER {trigger}")
    op.execute("DROP TABLE search_index")
