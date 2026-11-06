from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.modules.items.models import Item
from app.modules.locations.models import Location
from app.modules.locations.schemas import LocationCreate, LocationOut, LocationUpdate
from app.modules.tags import service as tags
from app.modules.tags.models import Tag


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
        tags=location.tags,
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


def inherited_tags(session: Session, location_id: int) -> list[Tag]:
    """The tags of a location and all its ancestors: what an item put there gets."""
    found: dict[int, Tag] = {}
    location: Location | None = get_location(session, location_id)
    while location is not None:
        for tag in location.tags:
            found.setdefault(tag.id, tag)
        location = session.get(Location, location.parent_id) if location.parent_id else None
    return list(found.values())


def _items_missing(session: Session, location_id: int, tag_id: int) -> list[Item]:
    """Items here or in a sub-location without the tag."""
    tags.get_tag(session, tag_id)
    query = select(Item).where(
        Item.location_id.in_(descendant_ids(session, location_id)),
        ~Item.tags.any(Tag.id == tag_id),
    )
    return list(session.scalars(query))


def count_items_missing_tag(session: Session, location_id: int, tag_id: int) -> int:
    get_location(session, location_id)
    return len(_items_missing(session, location_id, tag_id))


def tag_items(session: Session, location_id: int, tag_id: int) -> int:
    """Gives the tag to the items already here or below, for after adding it to the
    location (which on its own only affects items put here later). Returns how many."""
    get_location(session, location_id)
    tag = tags.get_tag(session, tag_id)
    items = _items_missing(session, location_id, tag_id)
    for item in items:
        item.tags.append(tag)
    session.commit()
    return len(items)


def list_locations(session: Session) -> list[LocationOut]:
    counts = _item_counts(session)
    locations = session.scalars(select(Location).order_by(func.lower(Location.name)))
    return [_to_out(location, counts) for location in locations]


def create_location(session: Session, data: LocationCreate) -> LocationOut:
    if data.parent_id is not None:
        get_location(session, data.parent_id)
    location = Location(
        name=data.name, parent_id=data.parent_id, tags=tags.get_tags(session, data.tag_ids)
    )
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
    if (tag_ids := changes.pop("tag_ids", None)) is not None:
        location.tags = tags.get_tags(session, tag_ids)
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
