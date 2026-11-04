from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text

from app.core import config
from app.core.config import BACKEND_DIR
from app.core.db import Base, create_db_engine, get_session, import_all_models
from app.modules.search.index import is_search_table


def alembic_config() -> Config:
    return Config(BACKEND_DIR / "alembic.ini")


def test_sqlite_pragmas():
    session = next(get_session())
    assert session.execute(text("PRAGMA foreign_keys")).scalar() == 1
    assert session.execute(text("PRAGMA journal_mode")).scalar() == "wal"
    assert session.execute(text("PRAGMA busy_timeout")).scalar() == 5000


def test_migrations_run_on_fresh_database(tmp_path, monkeypatch):
    monkeypatch.setattr(config.settings, "data_dir", tmp_path)
    cfg = alembic_config()

    command.upgrade(cfg, "head")
    engine = create_engine(config.settings.database_url)
    head = ScriptDirectory.from_config(cfg).get_current_head()
    with engine.connect() as conn:
        assert MigrationContext.configure(conn).get_current_revision() == head
    assert (tmp_path / "attachments").is_dir()

    command.downgrade(cfg, "base")
    assert inspect(engine).get_table_names() == ["alembic_version"]


def test_models_match_migrations(tmp_path, monkeypatch):
    """Fails when a model changes without a migration."""
    monkeypatch.setattr(config.settings, "data_dir", tmp_path)
    command.upgrade(alembic_config(), "head")
    import_all_models()
    engine = create_engine(config.settings.database_url)
    with engine.connect() as conn:
        context = MigrationContext.configure(
            conn,
            opts={"include_name": lambda name, type_, _: not is_search_table(name)},
        )
        assert compare_metadata(context, Base.metadata) == []


def _search_schema(engine) -> set[tuple[str, str]]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT name, sql FROM sqlite_master "
                "WHERE name LIKE 'search_index%' AND sql IS NOT NULL"
            )
        )
        return {(name, sql) for name, sql in rows}


def test_search_index_matches_migrations(tmp_path, monkeypatch):
    """The migrated search table and triggers match index.py, and no later migration
    lost a trigger by rebuilding a table."""
    monkeypatch.setattr(config.settings, "data_dir", tmp_path)
    command.upgrade(alembic_config(), "head")
    migrated = _search_schema(create_engine(config.settings.database_url))

    import_all_models()
    fresh = create_db_engine(f"sqlite:///{tmp_path / 'fresh.db'}")
    Base.metadata.create_all(fresh)
    expected = _search_schema(fresh)
    assert len(expected) == 15  # the table, its five shadow tables and nine triggers
    assert migrated == expected
