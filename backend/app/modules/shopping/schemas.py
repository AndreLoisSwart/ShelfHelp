from pydantic import BaseModel

from app.modules.items.schemas import ItemSummary, ProjectRef


class Zone(BaseModel):
    id: int
    name: str


class ShoppingItem(ItemSummary):
    # Open projects (not done or abandoned) the item is linked to.
    projects: list[ProjectRef]


class ShoppingList(BaseModel):
    """One zone's list. zone is null for items without a location."""

    zone: Zone | None
    items: list[ShoppingItem]
