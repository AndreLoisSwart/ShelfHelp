from pydantic import BaseModel, ConfigDict

from app.core.schemas import Name


class TagRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class TagOut(TagRef):
    item_count: int
    project_count: int


class TagCreate(BaseModel):
    name: Name


class TagUpdate(BaseModel):
    name: Name
