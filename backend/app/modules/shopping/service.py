"""The shopping list is computed from item statuses, never stored."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.items.models import Item, ItemStatus
from app.modules.items.schemas import ItemSummary, ProjectRef
from app.modules.locations.models import Location
from app.modules.projects.models import Project, ProjectItem, ProjectStatus
from app.modules.shopping.schemas import ShoppingItem, ShoppingList, Zone

TO_BUY = (ItemStatus.LOW, ItemStatus.OUT, ItemStatus.NEED)
CLOSED = (ProjectStatus.DONE, ProjectStatus.ABANDONED)


def _zone_of(locations: dict[int, Location]) -> dict[int, int]:
    """Each location's top-level ancestor."""

    def top(location_id: int) -> int:
        while (parent_id := locations[location_id].parent_id) is not None:
            location_id = parent_id
        return location_id

    return {location_id: top(location_id) for location_id in locations}


def _open_projects(session: Session, item_ids: list[int]) -> dict[int, list[ProjectRef]]:
    rows = session.execute(
        select(ProjectItem.item_id, Project)
        .join(Project)
        .where(ProjectItem.item_id.in_(item_ids), Project.status.not_in(CLOSED))
        .order_by(func.lower(Project.name))
    )
    result: dict[int, list[ProjectRef]] = {}
    for item_id, project in rows:
        ref = ProjectRef(id=project.id, name=project.name, status=project.status)
        result.setdefault(item_id, []).append(ref)
    return result


def shopping_lists(session: Session) -> list[ShoppingList]:
    """A list per zone, sorted by name, even when empty. "Unassigned" last, when not empty."""
    locations = {loc.id: loc for loc in session.scalars(select(Location))}
    zone_of = _zone_of(locations)
    items = list(
        session.scalars(select(Item).where(Item.status.in_(TO_BUY)).order_by(func.lower(Item.name)))
    )
    projects = _open_projects(session, [item.id for item in items])

    zones = sorted(
        (loc for loc in locations.values() if loc.parent_id is None),
        key=lambda loc: loc.name.lower(),
    )
    lists = {
        zone.id: ShoppingList(zone=Zone(id=zone.id, name=zone.name), items=[]) for zone in zones
    }
    unassigned = ShoppingList(zone=None, items=[])
    for item in items:
        entry = ShoppingItem(
            **ItemSummary.model_validate(item).model_dump(), projects=projects.get(item.id, [])
        )
        zone_id = zone_of.get(item.location_id) if item.location_id is not None else None
        (lists[zone_id] if zone_id is not None else unassigned).items.append(entry)
    return [*lists.values(), *([unassigned] if unassigned.items else [])]
