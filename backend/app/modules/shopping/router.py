from fastapi import APIRouter

from app.core.db import SessionDep
from app.modules.shopping import service
from app.modules.shopping.schemas import ShoppingList

router = APIRouter(prefix="/shopping", tags=["shopping"])


@router.get("")
def get_shopping_lists(session: SessionDep) -> list[ShoppingList]:
    """Every item that is low, out or needed, grouped by the zone of its location."""
    return service.shopping_lists(session)
