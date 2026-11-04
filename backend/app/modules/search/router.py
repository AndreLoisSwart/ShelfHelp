from typing import Annotated

from fastapi import APIRouter, Query

from app.core.db import SessionDep
from app.modules.search import service
from app.modules.search.schemas import SearchResults

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def search(session: SessionDep, q: Annotated[str, Query(max_length=200)] = "") -> SearchResults:
    """Up to 5 of each kind, best match first. Every word must match the start of a word."""
    return service.search(session, q)
