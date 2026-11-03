from typing import Annotated

from fastapi import APIRouter, Query

from app.core.db import SessionDep
from app.modules.items import service
from app.modules.items.models import ItemStatus
from app.modules.items.schemas import ItemCreate, ItemDetail, ItemSummary, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.get("")
def list_items(
    session: SessionDep,
    location_id: int | None = None,
    status: Annotated[list[ItemStatus] | None, Query()] = None,
    tag_id: Annotated[list[int] | None, Query()] = None,
) -> list[ItemSummary]:
    """location_id includes sub-locations. Several status or tag_id values match any of them."""
    items = service.list_items(session, location_id, status, tag_id)
    return [ItemSummary.model_validate(item) for item in items]


@router.post("", status_code=201)
def create_item(data: ItemCreate, session: SessionDep) -> ItemDetail:
    return ItemDetail.model_validate(service.create_item(session, data))


@router.get("/{item_id}")
def get_item(item_id: int, session: SessionDep) -> ItemDetail:
    return ItemDetail.model_validate(service.get_item(session, item_id))


@router.patch("/{item_id}")
def update_item(item_id: int, data: ItemUpdate, session: SessionDep) -> ItemDetail:
    return ItemDetail.model_validate(service.update_item(session, item_id, data))


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, session: SessionDep) -> None:
    service.delete_item(session, item_id)
