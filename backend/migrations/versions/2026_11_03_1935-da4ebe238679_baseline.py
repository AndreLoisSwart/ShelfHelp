"""baseline

Empty starting point. Tables arrive with their feature modules.

Revision ID: da4ebe238679
Revises:
Create Date: 2026-11-03 19:35:49.143301

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "da4ebe238679"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
