from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.modules import owners
from app.modules.links.models import Link
from app.modules.links.schemas import LinkCreate, LinkUpdate
from app.modules.owners import OwnerType


def get_link(session: Session, link_id: int) -> Link:
    link = session.get(Link, link_id)
    if link is None:
        raise NotFoundError(f"Link {link_id} not found")
    return link


def list_links(session: Session, owner_type: OwnerType, owner_id: int) -> list[Link]:
    owners.check_owner(session, owner_type, owner_id)
    query = select(Link).where(owners.owner_filter(Link, owner_type, owner_id)).order_by(Link.id)
    return list(session.scalars(query))


def create_link(session: Session, data: LinkCreate) -> Link:
    owners.check_owner(session, data.owner_type, data.owner_id)
    link = Link(url=data.url, title=data.title.strip())
    setattr(link, f"{data.owner_type}_id", data.owner_id)
    session.add(link)
    owners.touch_owner(session, data.owner_type, data.owner_id)
    session.commit()
    return link


def update_link(session: Session, link_id: int, data: LinkUpdate) -> Link:
    link = get_link(session, link_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(link, field, value.strip())
    owners.touch_owner(session, *owners.owner_of(link))
    session.commit()
    return link


def delete_link(session: Session, link_id: int) -> None:
    link = get_link(session, link_id)
    owners.touch_owner(session, *owners.owner_of(link))
    session.delete(link)
    session.commit()
