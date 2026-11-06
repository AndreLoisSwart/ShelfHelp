from fastapi import APIRouter

from app.core.db import SessionDep
from app.modules.shopping import service
from app.modules.shopping.schemas import ShoppingList

router = APIRouter(prefix="/shopping", tags=["shopping"])


@router.get("")
def get_shopping_lists(session: SessionDep, shop_id: int | None = None) -> list[ShoppingList]:
    """Every item that is low, out or needed, grouped by the zone of its location.

    shop_id narrows it to items sold at that shop, plus items with no shop set.
    """
    return service.shopping_lists(session, shop_id)
