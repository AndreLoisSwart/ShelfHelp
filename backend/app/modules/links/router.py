from fastapi import APIRouter

from app.core.db import SessionDep
from app.modules.links import service
from app.modules.links.schemas import LinkCreate, LinkOut, LinkUpdate
from app.modules.owners import OwnerType

router = APIRouter(prefix="/links", tags=["links"])


@router.get("")
def list_links(owner_type: OwnerType, owner_id: int, session: SessionDep) -> list[LinkOut]:
    """The links of one project, item or note, oldest first."""
    links = service.list_links(session, owner_type, owner_id)
    return [LinkOut.model_validate(link) for link in links]


@router.post("", status_code=201)
def create_link(data: LinkCreate, session: SessionDep) -> LinkOut:
    return LinkOut.model_validate(service.create_link(session, data))


@router.patch("/{link_id}")
def update_link(link_id: int, data: LinkUpdate, session: SessionDep) -> LinkOut:
    return LinkOut.model_validate(service.update_link(session, link_id, data))


@router.delete("/{link_id}", status_code=204)
def delete_link(link_id: int, session: SessionDep) -> None:
    service.delete_link(session, link_id)
