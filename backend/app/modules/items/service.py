from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import utcnow
from app.core.errors import ConflictError, NotFoundError
from app.modules.items.models import Item, ItemStatus
from app.modules.items.schemas import ItemCreate, ItemUpdate
from app.modules.locations import service as locations
from app.modules.tags import service as tags
from app.modules.tags.models import Tag


def get_item(session: Session, item_id: int) -> Item:
    item = session.get(Item, item_id)
    if item is None:
        raise NotFoundError(f"Item {item_id} not found")
    return item


def list_items(
    session: Session,
    location_id: int | None = None,
    statuses: list[ItemStatus] | None = None,
    tag_ids: list[int] | None = None,
) -> list[Item]:
    query = select(Item).order_by(func.lower(Item.name))
    if location_id is not None:
        # Includes everything stored in sub-locations.
        query = query.where(Item.location_id.in_(locations.descendant_ids(session, location_id)))
    if statuses:
        query = query.where(Item.status.in_(statuses))
    if tag_ids:
        query = query.where(Item.tags.any(Tag.id.in_(tag_ids)))
    return list(session.scalars(query))


def _check_parent(session: Session, item: Item | None, parent_id: int) -> None:
    parent = get_item(session, parent_id)
    if item is None:
        return
    # Walk up from the new parent: meeting the item itself would make a cycle.
    while parent is not None:
        if parent.id == item.id:
            raise ConflictError("An item can't be its own parent or sit under its own child")
        parent = parent.parent


def create_item(session: Session, data: ItemCreate) -> Item:
    if data.parent_id is not None:
        _check_parent(session, None, data.parent_id)
    if data.location_id is not None:
        locations.get_location(session, data.location_id)
    item = Item(
        name=data.name,
        status=data.status,
        description=data.description,
        parent_id=data.parent_id,
        location_id=data.location_id,
        tags=tags.get_tags(session, data.tag_ids),
    )
    session.add(item)
    session.commit()
    return item


def update_item(session: Session, item_id: int, data: ItemUpdate) -> Item:
    item = get_item(session, item_id)
    changes = data.model_dump(exclude_unset=True)
    if (parent_id := changes.get("parent_id")) is not None:
        _check_parent(session, item, parent_id)
    if (location_id := changes.get("location_id")) is not None:
        locations.get_location(session, location_id)
    if (tag_ids := changes.pop("tag_ids", None)) is not None:
        item.tags = tags.get_tags(session, tag_ids)
    for field, value in changes.items():
        setattr(item, field, value)
    item.updated_at = utcnow()
    session.commit()
    return item


def delete_item(session: Session, item_id: int) -> None:
    # Children become top-level items (ON DELETE SET NULL).
    session.delete(get_item(session, item_id))
    session.commit()
