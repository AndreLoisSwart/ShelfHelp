from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.modules.items.models import Item
from app.modules.locations.models import Location
from app.modules.locations.schemas import LocationCreate, LocationOut, LocationUpdate


def _item_counts(session: Session) -> dict[int, int]:
    rows = session.execute(
        select(Item.location_id, func.count())
        .where(Item.location_id.is_not(None))
        .group_by(Item.location_id)
    ).all()
    return dict(rows)


def _to_out(location: Location, counts: dict[int, int]) -> LocationOut:
    return LocationOut(
        id=location.id,
        name=location.name,
        parent_id=location.parent_id,
        item_count=counts.get(location.id, 0),
    )


def get_location(session: Session, location_id: int) -> Location:
    location = session.get(Location, location_id)
    if location is None:
        raise NotFoundError(f"Location {location_id} not found")
    return location


def descendant_ids(session: Session, location_id: int) -> set[int]:
    """The location and everything below it. The table is small, so walk it in memory."""
    children: dict[int | None, list[int]] = {}
    for id_, parent_id in session.execute(select(Location.id, Location.parent_id)):
        children.setdefault(parent_id, []).append(id_)
    found, stack = set(), [location_id]
    while stack:
        current = stack.pop()
        found.add(current)
        stack.extend(children.get(current, []))
    return found


def list_locations(session: Session) -> list[LocationOut]:
    counts = _item_counts(session)
    locations = session.scalars(select(Location).order_by(func.lower(Location.name)))
    return [_to_out(location, counts) for location in locations]


def create_location(session: Session, data: LocationCreate) -> LocationOut:
    if data.parent_id is not None:
        get_location(session, data.parent_id)
    location = Location(name=data.name, parent_id=data.parent_id)
    session.add(location)
    session.commit()
    return _to_out(location, _item_counts(session))


def update_location(session: Session, location_id: int, data: LocationUpdate) -> LocationOut:
    location = get_location(session, location_id)
    changes = data.model_dump(exclude_unset=True)
    if (parent_id := changes.get("parent_id")) is not None:
        get_location(session, parent_id)
        if parent_id in descendant_ids(session, location_id):
            raise ConflictError("A location can't be moved inside itself")
    for field, value in changes.items():
        setattr(location, field, value)
    session.commit()
    return _to_out(location, _item_counts(session))


def delete_location(session: Session, location_id: int) -> None:
    location = get_location(session, location_id)
    if session.scalar(select(func.count()).where(Location.parent_id == location_id)):
        raise ConflictError("Move or delete its sub-locations first")
    if item_count := _item_counts(session).get(location_id, 0):
        noun = "item is" if item_count == 1 else "items are"
        raise ConflictError(f"{item_count} {noun} stored here. Move them first")
    session.delete(location)
    session.commit()
