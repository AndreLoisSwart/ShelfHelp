from fastapi import APIRouter

from app.core.db import SessionDep
from app.modules.shops import service
from app.modules.shops.schemas import ShopCreate, ShopOut, ShopUpdate

router = APIRouter(prefix="/shops", tags=["shops"])


@router.get("")
def list_shops(session: SessionDep) -> list[ShopOut]:
    return service.list_shops(session)


@router.post("", status_code=201)
def create_shop(data: ShopCreate, session: SessionDep) -> ShopOut:
    return service.create_shop(session, data)


@router.patch("/{shop_id}")
def update_shop(shop_id: int, data: ShopUpdate, session: SessionDep) -> ShopOut:
    return service.update_shop(session, shop_id, data)


@router.delete("/{shop_id}", status_code=204)
def delete_shop(shop_id: int, session: SessionDep) -> None:
    service.delete_shop(session, shop_id)
