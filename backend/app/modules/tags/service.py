from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.modules.items.models import item_tags
from app.modules.tags.models import Tag
from app.modules.tags.schemas import TagCreate, TagOut, TagUpdate


def _item_counts(session: Session) -> dict[int, int]:
    rows = session.execute(
        select(item_tags.c.tag_id, func.count()).group_by(item_tags.c.tag_id)
    ).all()
    return dict(rows)


def _to_out(tag: Tag, counts: dict[int, int]) -> TagOut:
    return TagOut(id=tag.id, name=tag.name, item_count=counts.get(tag.id, 0))


def _check_unique(session: Session, name: str, exclude_id: int | None = None) -> None:
    # The NOCASE column collation makes this comparison case-insensitive.
    existing = session.scalar(select(Tag).where(Tag.name == name))
    if existing and existing.id != exclude_id:
        raise ConflictError(f'A tag named "{existing.name}" already exists')


def get_tag(session: Session, tag_id: int) -> Tag:
    tag = session.get(Tag, tag_id)
    if tag is None:
        raise NotFoundError(f"Tag {tag_id} not found")
    return tag


def get_tags(session: Session, tag_ids: list[int]) -> list[Tag]:
    return [get_tag(session, tag_id) for tag_id in dict.fromkeys(tag_ids)]


def list_tags(session: Session) -> list[TagOut]:
    counts = _item_counts(session)
    tags = session.scalars(select(Tag).order_by(func.lower(Tag.name)))
    return [_to_out(tag, counts) for tag in tags]


def create_tag(session: Session, data: TagCreate) -> TagOut:
    _check_unique(session, data.name)
    tag = Tag(name=data.name)
    session.add(tag)
    session.commit()
    return _to_out(tag, _item_counts(session))


def update_tag(session: Session, tag_id: int, data: TagUpdate) -> TagOut:
    tag = get_tag(session, tag_id)
    _check_unique(session, data.name, exclude_id=tag_id)
    tag.name = data.name
    session.commit()
    return _to_out(tag, _item_counts(session))


def delete_tag(session: Session, tag_id: int) -> None:
    # Links to items go with it (ON DELETE CASCADE).
    session.delete(get_tag(session, tag_id))
    session.commit()
