"""The MCP server: Shelf-help's tools for Claude and other MCP clients.

Tools call the same router functions as the REST API, so every rule in the service
layer applies (last touched, inbox, readiness) and Claude sees what the app shows.

Deliberately left out for now (docs/future-enhancements.md):
- Deletes of any kind. Deleting stays a job for the app.
- Replacing free text: note bodies and descriptions can be added to, not overwritten.
- Clearing a field (e.g. an item's location): None means "leave unchanged".
"""

import functools
import inspect
from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Annotated, Literal

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.modules.dashboard import router as dashboard
from app.modules.dashboard.schemas import Dashboard
from app.modules.inbox import router as inbox
from app.modules.inbox.schemas import Inbox
from app.modules.items import router as items
from app.modules.items.models import ItemStatus
from app.modules.items.schemas import ItemCreate, ItemDetail, ItemSummary, ItemUpdate
from app.modules.links import router as links
from app.modules.links.schemas import LinkCreate, LinkOut
from app.modules.locations import router as locations
from app.modules.locations.schemas import LocationOut, LocationUpdate
from app.modules.notes import router as notes
from app.modules.notes.schemas import NoteCreate, NoteDetail, NoteSummary, NoteUpdate
from app.modules.owners import OwnerType
from app.modules.projects import router as projects
from app.modules.projects.models import ProjectStatus, Requirement
from app.modules.projects.schemas import (
    ProjectCreate,
    ProjectDetail,
    ProjectItemLink,
    ProjectItemOut,
    ProjectSummary,
    ProjectUpdate,
)
from app.modules.search import router as search_router
from app.modules.search.schemas import SearchResults
from app.modules.shopping import router as shopping
from app.modules.shopping.schemas import ShoppingList
from app.modules.shops import router as shops
from app.modules.shops.schemas import ShopCreate, ShopOut
from app.modules.tags import router as tags
from app.modules.tags.schemas import TagCreate, TagOut

INSTRUCTIONS = """\
Shelf-help is the user's personal manager for projects, the items they need, and notes.

- Projects have a status (someday, planned, active, paused, done, abandoned), a next step,
  linked items, notes and links. Readiness counts linked required items on hand.
- Items are standalone things (tools, materials, household goods) with a status: have,
  low, out or need (to get). Low, out and need items make up the shopping list, grouped by
  zone (the top-level location). Items are linked to projects, never owned by them.
- Items can list the shops that sell them. Filter the shopping list by shop to answer
  "what do I need from <shop>?"; items with no shop set are included, since they could
  be bought anywhere.
- Locations form a tree; tags label projects and items. Look up ids with list_locations,
  list_tags and list_shops before using them.
- Tags given to a location are added to items put there (or in a sub-location), and parts
  get their parent item's tags. Tags are only ever added this way, never removed.
- get_project lists suggested_tags: tags on its items the project lacks. Offer them to
  the user rather than adding them unasked.
- The inbox holds records waiting to be sorted. Fill in details yourself when you can.
  Set in_inbox=true when creating something you're unsure about, so the user reviews it.
- Search before creating, to avoid duplicates.
- You can add to notes (append_to_note) but not rewrite or delete them, and nothing can
  be deleted through these tools: ask the user to do that in the app.
"""

READ = ToolAnnotations(readOnlyHint=True)
WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False)

MARK_START, MARK_END = "\x02", "\x03"

SessionOpener = Callable[[], AbstractContextManager[Session]]


class ProjectContext(BaseModel):
    project: ProjectDetail
    items: list[ProjectItemOut]
    notes: list[NoteSummary]
    links: list[LinkOut]


class ItemContext(BaseModel):
    item: ItemDetail
    links: list[LinkOut]


class NoteContext(BaseModel):
    note: NoteDetail
    links: list[LinkOut]


def _unmarked(results: SearchResults) -> SearchResults:
    """Search marks matched words for highlighting; that's noise to a model."""

    def clean(text: str) -> str:
        return text.replace(MARK_START, "").replace(MARK_END, "")

    def hits(group):
        return [
            h.model_copy(update={"title": clean(h.title), "snippet": clean(h.snippet)})
            for h in group
        ]

    return SearchResults(
        projects=hits(results.projects), items=hits(results.items), notes=hits(results.notes)
    )


def _explained(fn):
    """Lets the model read why a call was refused (a missing record, a broken rule,
    an invalid value). The SDK hides the text of other exceptions, as crashes."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (NotFoundError, ConflictError) as e:
            raise ToolError(str(e)) from e
        except ValidationError as e:
            problems = "; ".join(
                f"{'.'.join(map(str, err['loc']))}: {err['msg'].removeprefix('Value error, ')}"
                for err in e.errors()
            )
            raise ToolError(problems) from e

    return wrapper


def _set(**fields) -> dict:
    """Only the fields given, for partial updates."""
    return {name: value for name, value in fields.items() if value is not None}


def build_server(open_session: SessionOpener) -> MCPServer:
    server = MCPServer(name="Shelf-help", instructions=INSTRUCTIONS)

    def tool(annotations: ToolAnnotations):
        """Registers a tool, its docstring (without code indentation) as the description."""

        def register(fn):
            description = inspect.cleandoc(fn.__doc__ or "")
            return server.tool(description=description, annotations=annotations)(_explained(fn))

        return register

    # --- Finding things ---

    @tool(READ)
    def search(query: Annotated[str, Field(max_length=200)]) -> SearchResults:
        """Full-text search over project names, next steps and descriptions, item names and
        descriptions, and note titles and bodies. Every word must match the start of a word.
        Up to 5 results of each kind, best first."""
        with open_session() as session:
            return _unmarked(search_router.search(session, query))

    @tool(READ)
    def get_dashboard() -> Dashboard:
        """Active projects with next steps, items running low, and projects gone quiet."""
        with open_session() as session:
            return dashboard.get_dashboard(session)

    @tool(READ)
    def get_shopping_list(shop_id: int | None = None) -> list[ShoppingList]:
        """Everything low, out or needed, grouped by zone, with the projects each is for.
        shop_id narrows it to items sold at that shop, plus items with no shop set."""
        with open_session() as session:
            return shopping.get_shopping_lists(session, shop_id)

    @tool(READ)
    def get_inbox() -> Inbox:
        """Records waiting to be sorted, newest first."""
        with open_session() as session:
            return inbox.get_inbox(session)

    @tool(READ)
    def list_locations() -> list[LocationOut]:
        """All locations with their tags. parent_id null means a zone (top-level location)."""
        with open_session() as session:
            return locations.list_locations(session)

    @tool(WRITE)
    def set_location_tags(
        location_id: int, tag_ids: list[int], tag_existing_items: bool = False
    ) -> LocationOut:
        """Replaces a location's tags. Items put there or in a sub-location from now on get
        them. tag_existing_items also adds them to the items already there; otherwise
        existing items are left alone. Removing a tag never removes it from items."""
        with open_session() as session:
            location = locations.update_location(
                location_id, LocationUpdate(tag_ids=tag_ids), session
            )
            if tag_existing_items:
                for tag_id in tag_ids:
                    locations.tag_items(location_id, tag_id, session)
                location = next(
                    loc for loc in locations.list_locations(session) if loc.id == location_id
                )
            return location

    @tool(READ)
    def list_tags() -> list[TagOut]:
        """All tags, with how many items and projects use each."""
        with open_session() as session:
            return tags.list_tags(session)

    @tool(READ)
    def list_shops() -> list[ShopOut]:
        """All shops, with how many items each sells."""
        with open_session() as session:
            return shops.list_shops(session)

    # --- Projects ---

    @tool(READ)
    def list_projects(
        status: list[ProjectStatus] | None = None, tag_ids: list[int] | None = None
    ) -> list[ProjectSummary]:
        """Projects, most recently touched first. Filters match any of the values given."""
        with open_session() as session:
            return projects.list_projects(session, status, tag_ids)

    @tool(READ)
    def get_project(project_id: int) -> ProjectContext:
        """A project with its description, linked items, notes and links."""
        with open_session() as session:
            return ProjectContext(
                project=projects.get_project(project_id, session),
                items=projects.list_project_items(project_id, session),
                notes=notes.list_notes(session, project_id),
                links=links.list_links(OwnerType.PROJECT, project_id, session),
            )

    @tool(WRITE)
    def create_project(
        name: str,
        status: ProjectStatus = ProjectStatus.SOMEDAY,
        next_step: str = "",
        description_md: str = "",
        tag_ids: list[int] | None = None,
        in_inbox: bool = False,
    ) -> ProjectDetail:
        """Creates a project. description_md is markdown."""
        data = ProjectCreate(
            name=name,
            status=status,
            next_step=next_step,
            description_md=description_md,
            tag_ids=tag_ids or [],
            in_inbox=in_inbox,
        )
        with open_session() as session:
            return projects.create_project(data, session)

    @tool(WRITE)
    def update_project(
        project_id: int,
        name: str | None = None,
        status: ProjectStatus | None = None,
        next_step: str | None = None,
        tag_ids: list[int] | None = None,
    ) -> ProjectDetail:
        """Changes only the fields given. tag_ids replaces the project's tags.
        The description can't be changed here."""
        data = ProjectUpdate(**_set(name=name, status=status, next_step=next_step, tag_ids=tag_ids))
        with open_session() as session:
            return projects.update_project(project_id, data, session)

    @tool(WRITE)
    def link_item_to_project(
        project_id: int,
        item_id: int,
        requirement: Requirement = Requirement.REQUIRED,
        note: Annotated[str, Field(max_length=200)] = "",
    ) -> ProjectItemOut:
        """Links an item to a project, or updates the link's requirement and note.
        note is short, e.g. "need 2"."""
        data = ProjectItemLink(requirement=requirement, note=note)
        with open_session() as session:
            return projects.link_project_item(project_id, item_id, data, session)

    @tool(WRITE)
    def unlink_item_from_project(project_id: int, item_id: int) -> str:
        """Removes the link between an item and a project. Both stay as they are."""
        with open_session() as session:
            projects.unlink_project_item(project_id, item_id, session)
        return "Unlinked"

    # --- Items ---

    @tool(READ)
    def list_items(
        location_id: int | None = None,
        status: list[ItemStatus] | None = None,
        tag_ids: list[int] | None = None,
    ) -> list[ItemSummary]:
        """Items by name. location_id includes its sub-locations. Filters match any value."""
        with open_session() as session:
            return items.list_items(session, location_id, status, tag_ids)

    @tool(READ)
    def get_item(item_id: int) -> ItemContext:
        """An item with its description, parent and child items, linked projects and links."""
        with open_session() as session:
            return ItemContext(
                item=items.get_item(item_id, session),
                links=links.list_links(OwnerType.ITEM, item_id, session),
            )

    @tool(WRITE)
    def create_item(
        name: str,
        status: ItemStatus = ItemStatus.HAVE,
        description: str = "",
        location_id: int | None = None,
        parent_id: int | None = None,
        tag_ids: list[int] | None = None,
        shop_ids: list[int] | None = None,
        in_inbox: bool = False,
    ) -> ItemDetail:
        """Creates an item. parent_id makes it part of another item (e.g. a blade for a saw).
        To link it to a project, use link_item_to_project afterwards."""
        data = ItemCreate(
            name=name,
            status=status,
            description=description,
            location_id=location_id,
            parent_id=parent_id,
            tag_ids=tag_ids or [],
            shop_ids=shop_ids or [],
            in_inbox=in_inbox,
        )
        with open_session() as session:
            return items.create_item(data, session)

    @tool(WRITE)
    def update_item(
        item_id: int,
        name: str | None = None,
        status: ItemStatus | None = None,
        location_id: int | None = None,
        parent_id: int | None = None,
        tag_ids: list[int] | None = None,
        shop_ids: list[int] | None = None,
    ) -> ItemDetail:
        """Changes only the fields given. tag_ids and shop_ids replace the item's tags
        and shops.
        The description can't be changed here."""
        data = ItemUpdate(
            **_set(
                name=name,
                status=status,
                location_id=location_id,
                parent_id=parent_id,
                tag_ids=tag_ids,
                shop_ids=shop_ids,
            )
        )
        with open_session() as session:
            return items.update_item(item_id, data, session)

    # --- Notes ---

    @tool(READ)
    def list_notes(project_id: int | None = None, no_project: bool = False) -> list[NoteSummary]:
        """Notes, most recently updated first, with a short excerpt.
        no_project lists only notes that don't belong to a project."""
        with open_session() as session:
            return notes.list_notes(session, project_id, no_project)

    @tool(READ)
    def get_note(note_id: int) -> NoteContext:
        """A note's full markdown body, its project and links."""
        with open_session() as session:
            return NoteContext(
                note=notes.get_note(note_id, session),
                links=links.list_links(OwnerType.NOTE, note_id, session),
            )

    @tool(WRITE)
    def create_note(
        title: str, body_md: str = "", project_id: int | None = None, in_inbox: bool = False
    ) -> NoteDetail:
        """Creates a note. body_md is markdown: headings, lists, `- [ ]` checkboxes, tables."""
        data = NoteCreate(title=title, body_md=body_md, project_id=project_id, in_inbox=in_inbox)
        with open_session() as session:
            return notes.create_note(data, session)

    @tool(WRITE)
    def append_to_note(note_id: int, text_md: str) -> NoteDetail:
        """Adds markdown to the end of a note, as a new paragraph. The existing text is kept."""
        with open_session() as session:
            body = notes.get_note(note_id, session).body_md.rstrip()
            addition = text_md.strip()
            new_body = f"{body}\n\n{addition}\n" if body else f"{addition}\n"
            return notes.update_note(note_id, NoteUpdate(body_md=new_body), session)

    @tool(WRITE)
    def update_note(
        note_id: int, title: str | None = None, project_id: int | None = None
    ) -> NoteDetail:
        """Renames a note or moves it to a project. The body can only be added to,
        with append_to_note."""
        data = NoteUpdate(**_set(title=title, project_id=project_id))
        with open_session() as session:
            return notes.update_note(note_id, data, session)

    # --- Inbox, tags, shops and links ---

    @tool(WRITE)
    def mark_sorted(record_type: Literal["project", "item", "note"], record_id: int) -> str:
        """Takes a record out of the inbox once its details are filled in."""
        with open_session() as session:
            if record_type == "project":
                projects.update_project(record_id, ProjectUpdate(in_inbox=False), session)
            elif record_type == "item":
                items.update_item(record_id, ItemUpdate(in_inbox=False), session)
            else:
                notes.update_note(record_id, NoteUpdate(in_inbox=False), session)
        return f"Sorted {record_type} {record_id}"

    @tool(WRITE)
    def create_tag(name: str) -> TagOut:
        """Creates a tag, for use in tag_ids. Fails if one with that name exists."""
        with open_session() as session:
            return tags.create_tag(TagCreate(name=name), session)

    @tool(WRITE)
    def create_shop(name: str) -> ShopOut:
        """Creates a shop, for use in shop_ids. Fails if one with that name exists."""
        with open_session() as session:
            return shops.create_shop(ShopCreate(name=name), session)

    @tool(WRITE)
    def add_link(owner_type: OwnerType, owner_id: int, url: str, title: str = "") -> LinkOut:
        """Adds a web link (http or https) to a project, item or note."""
        data = LinkCreate(owner_type=owner_type, owner_id=owner_id, url=url, title=title)
        with open_session() as session:
            return links.create_link(data, session)

    return server
