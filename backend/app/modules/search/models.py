from sqlalchemy import event

from app.core.db import Base
from app.modules.search.index import create_statements

# No mapped tables: the index is an FTS5 table plus triggers. Create them alongside the
# other tables (tests build their databases this way; real ones use the migration).


@event.listens_for(Base.metadata, "after_create")
def _create_search_index(_target, connection, **_kw) -> None:
    for statement in create_statements():
        connection.exec_driver_sql(statement)
