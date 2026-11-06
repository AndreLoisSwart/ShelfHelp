from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.modules.items.models import item_shops
from app.modules.shops.models import Shop
from app.modules.shops.schemas import ShopCreate, ShopOut, ShopUpdate


def _counts(session: Session) -> dict[int, int]:
    """How many items each shop sells."""
    query = select(item_shops.c.shop_id, func.count()).group_by(item_shops.c.shop_id)
    return dict(session.execute(query).all())


def _to_out(shop: Shop, counts: dict[int, int]) -> ShopOut:
    return ShopOut(id=shop.id, name=shop.name, item_count=counts.get(shop.id, 0))


def _check_unique(session: Session, name: str, exclude_id: int | None = None) -> None:
    # The NOCASE column collation makes this comparison case-insensitive.
    existing = session.scalar(select(Shop).where(Shop.name == name))
    if existing and existing.id != exclude_id:
        raise ConflictError(f'A shop named "{existing.name}" already exists')


def get_shop(session: Session, shop_id: int) -> Shop:
    shop = session.get(Shop, shop_id)
    if shop is None:
        raise NotFoundError(f"Shop {shop_id} not found")
    return shop


def get_shops(session: Session, shop_ids: list[int]) -> list[Shop]:
    # By name, as they load from the database, so a fresh save reads the same.
    found = [get_shop(session, shop_id) for shop_id in dict.fromkeys(shop_ids)]
    return sorted(found, key=lambda shop: shop.name.lower())


def list_shops(session: Session) -> list[ShopOut]:
    counts = _counts(session)
    shops = session.scalars(select(Shop).order_by(func.lower(Shop.name)))
    return [_to_out(shop, counts) for shop in shops]


def create_shop(session: Session, data: ShopCreate) -> ShopOut:
    _check_unique(session, data.name)
    shop = Shop(name=data.name)
    session.add(shop)
    session.commit()
    return _to_out(shop, _counts(session))


def update_shop(session: Session, shop_id: int, data: ShopUpdate) -> ShopOut:
    shop = get_shop(session, shop_id)
    _check_unique(session, data.name, exclude_id=shop_id)
    shop.name = data.name
    session.commit()
    return _to_out(shop, _counts(session))


def delete_shop(session: Session, shop_id: int) -> None:
    # Its links to items go with it (ON DELETE CASCADE).
    session.delete(get_shop(session, shop_id))
    session.commit()
