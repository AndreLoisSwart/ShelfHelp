from pydantic import BaseModel, ConfigDict

from app.core.schemas import Name


class ShopRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ShopOut(ShopRef):
    item_count: int


class ShopCreate(BaseModel):
    name: Name


class ShopUpdate(BaseModel):
    name: Name
