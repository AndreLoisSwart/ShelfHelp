from fastapi import APIRouter

from app.core.db import SessionDep
from app.modules.locations import service
from app.modules.locations.schemas import LocationCreate, LocationOut, LocationUpdate

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("")
def list_locations(session: SessionDep) -> list[LocationOut]:
    return service.list_locations(session)


@router.post("", status_code=201)
def create_location(data: LocationCreate, session: SessionDep) -> LocationOut:
    return service.create_location(session, data)


@router.patch("/{location_id}")
def update_location(location_id: int, data: LocationUpdate, session: SessionDep) -> LocationOut:
    return service.update_location(session, location_id, data)


@router.delete("/{location_id}", status_code=204)
def delete_location(location_id: int, session: SessionDep) -> None:
    service.delete_location(session, location_id)
