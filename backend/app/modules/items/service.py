from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import utcnow
from app.core.errors import ConflictError, NotFoundError
from app.modules.attachments import storage
from app.modules.attachments.models import Attachment
from app.modules.items.models import Item, ItemStatus
from app.modules.items.schemas import ItemCreate, ItemProjectOut, ItemUpdate, ProjectRef
from app.modules.locations import service as locations
from app.modules.projects import service as projects
from app.modules.projects.models import Project, ProjectItem
from app.modules.shops import service as shops
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


def _with(current: list[Tag], extra: list[Tag]) -> list[Tag]:
    """current plus any of extra it lacks, kept by name."""
    have = {tag.id for tag in current}
    merged = current + [tag for tag in extra if tag.id not in have]
    return sorted(merged, key=lambda tag: tag.name.lower())


def _inherited(session: Session, location_id: int | None, parent_id: int | None) -> list[Tag]:
    """Tags an item picks up from where it's put and from the item it's part of."""
    found: list[Tag] = []
    if location_id is not None:
        found += locations.inherited_tags(session, location_id)
    if parent_id is not None:
        found += get_item(session, parent_id).tags
    return found


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
        tags=_with(
            tags.get_tags(session, data.tag_ids),
            _inherited(session, data.location_id, data.parent_id),
        ),
        shops=shops.get_shops(session, data.shop_ids),
        in_inbox=data.in_inbox,
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
    if (shop_ids := changes.pop("shop_ids", None)) is not None:
        item.shops = shops.get_shops(session, shop_ids)
    # Moving it, or making it part of another item, adds the tags that come with that.
    # Never removes any: they may have been added by hand.
    moved_to = (
        changes.get("location_id") if changes.get("location_id") != item.location_id else None
    )
    new_parent = changes.get("parent_id") if changes.get("parent_id") != item.parent_id else None
    if extra := _inherited(session, moved_to, new_parent):
        item.tags = _with(list(item.tags), extra)
    for field, value in changes.items():
        setattr(item, field, value)
    item.updated_at = utcnow()
    session.commit()
    return item


def linked_projects(session: Session, item_id: int) -> list[ItemProjectOut]:
    rows = session.execute(
        select(Project, ProjectItem)
        .join(ProjectItem)
        .where(ProjectItem.item_id == item_id)
        .order_by(func.lower(Project.name))
    )
    return [
        ItemProjectOut(
            project=ProjectRef(id=project.id, name=project.name, status=project.status),
            requirement=link.requirement,
            note=link.note,
        )
        for project, link in rows
    ]


def delete_item(session: Session, item_id: int) -> None:
    item = get_item(session, item_id)
    # Its project links go with it (ON DELETE CASCADE), which counts as touching those projects.
    projects.touch_projects_using(session, item_id)
    # Children become top-level items (ON DELETE SET NULL). Links and attachments go with
    # it (ON DELETE CASCADE); their files are removed once the delete is committed.
    files = storage.stored_paths_of(session, Attachment.item_id, item_id)
    session.delete(item)
    session.commit()
    storage.remove_files(files)
