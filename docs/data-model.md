# Data model

## Tables

```
Project      id, name, description_md, status, next_step,
             in_inbox, created_at, updated_at, last_touched_at

Note         id, project_id (nullable → Project), title, body_md,
             in_inbox, created_at, updated_at

Item         id, name, description, status,
             parent_id (nullable → Item), location_id (nullable → Location),
             in_inbox, created_at, updated_at

Location     id, name, parent_id (nullable → Location)

ProjectItem  project_id, item_id, requirement, note (up to 200 characters)
             PK (project_id, item_id)

Tag          id, name (unique, ignoring case)
ProjectTag   project_id, tag_id
ItemTag      item_id, tag_id
LocationTag  location_id, tag_id

Shop         id, name (unique, ignoring case)
ItemShop     item_id, shop_id

Link         id, url, title,
             project_id | item_id | note_id   (exactly one set)

Attachment   id, original_filename, mime_type, size, stored_path, created_at,
             project_id | item_id | note_id   (exactly one set)

AppSettings  id (always 1), stale_after_days (default 21, 7 to 365)
```

`AppSettings` is a single row holding app-wide preferences, shared by every device. It is created with the defaults the first time it is read.

## Enums

| Enum | Values |
|---|---|
| `Project.status` | `someday`, `planned`, `active`, `paused`, `done`, `abandoned` |
| `Item.status` | `have`, `low`, `out`, `need` |
| `ProjectItem.requirement` | `required`, `nice_to_have` |

## Rules

**Inbox**
- Quick-add creates the real record (Project, Item or Note) with `in_inbox = true`. There is no separate capture table.
- The inbox shows every record with `in_inbox = true`, newest first. Only an explicit "Done" clears the flag, from the inbox or the record's page; filling in details doesn't, so nothing leaves the inbox by accident.
- Quick-add sets the type and name, plus Have or Need to get for an item. Projects start as `someday`.
- Inbox records still count everywhere else, including search and the shopping list.

**Items**
- An item can list any number of shops it can be bought from. None means "not set yet", not "nowhere". Deleting a shop removes it from its items.
- Items are always created standalone. Linking to a project is a separate action (through `ProjectItem`).
- `parent_id` allows item hierarchy (e.g. table saw → blades, belts). The schema supports it in V1, while the UI only needs to show it simply.
- Prevent cycles in `parent_id`.
- Deleting an item makes its children top-level items (`parent_id` is set to null).
- New items default to status `have`. `description` is plain text and defaults to empty.
- For a `need` item, `location_id` means *where it will live*. That decides which shopping list it appears on.

**Locations**
- A location's tags (and those of its ancestors) are copied to an item when it is created there or moved there, never linked: the item can drop them, and changing a location's tags doesn't change existing items. Settings offers to tag the items already there after a tag is added (`POST /api/locations/{id}/tag-items/{tag_id}`).
- Moving an item, or making it part of another item, only ever adds tags. A part also gets its parent item's tags.
- Locations form a tree. Top-level locations (no parent) are zones, e.g. Home and Workshop.
- Filtering by a location includes all of its descendants.
- Prevent cycles. Block deleting a location that still has items or children, or require them to be reassigned first.

**Projects**
- New projects default to status `someday`.
- `next_step` is a single line of up to 500 characters and may be empty.
- Lists are ordered by `last_touched_at`, most recent first.

**Item links**
- Linking an item that is already linked updates its requirement and note instead.
- Deleting a project or an item removes its links. Deleting an item touches the projects it was linked to.
- An item created from a project's "Link item" picker starts as `need`, so it lands on the shopping list.

**Notes**
- `body_md` is stored exactly as the editor saves it. The editor normalises style (e.g. `*` bullets become `-`), so a note may be reformatted the first time it is saved.
- Creating, editing or deleting a note touches its project. Moving a note touches both projects.
- Deleting a project keeps its notes, without a project (`project_id` is set to null).

**Tags**
- Tag names are unique ignoring case, so "Wood" and "wood" are the same tag.
- Deleting a tag removes it from every item and project.

**Links and attachments**
- Each record belongs to exactly one of project, item or note, enforced with a CHECK constraint across the three nullable foreign keys.
- Deleting the owner deletes its links and attachments. For attachments, the service also removes the file from disk.
- Attachment files are stored in `/data/attachments/` under generated names. The original filename is kept in the database.
- The API names an owner as `owner_type` (`project`, `item` or `note`) plus `owner_id`. The shared rules are in `backend/app/modules/owners.py`.
- Changes to a project's links or attachments touch it, and so do changes to those of its notes.
- Links must be `http://` or `https://`. Other schemes, like `javascript:`, could run code when clicked.
- Uploads are limited to 50 MB per file (`SHELF_MAX_UPLOAD_MB`).
- **Serving files safely:** behind Ingress, files come from Home Assistant's own origin, so a file the browser runs as a page could act with the user's HA login. Only PDFs and PNG, JPEG, GIF and WebP images open in the browser. Everything else downloads as `application/octet-stream`. All file responses send `X-Content-Type-Options: nosniff`, and images also send a sandboxing Content-Security-Policy. The type comes from the file extension, not the browser's claim.
- File responses are revalidated on every request (`no-cache`), because SQLite can reuse a deleted attachment's id.

**Last touched**
- `Project.last_touched_at` is set by the service layer whenever any of the following change:
  - the project itself
  - any of its notes
  - its item links
  - its links or attachments
- Each module that changes something attached to a project calls `projects.service.touch()`.
- "Stale" means an `active` or `paused` project whose `last_touched_at` is older than a threshold. The threshold is `AppSettings.stale_after_days`, set in Settings, and defaults to 3 weeks.

**Computed, never stored**
- **Suggested project tags:** tags on a project's linked items that the project lacks, most used first, up to 5. Offered on the project's Overview tab, never added automatically.
- **Readiness:** for a project, the count of `required` linked items with status `have` or `low`, out of all `required` linked items. Nice-to-have items are shown separately.
- **Shopping list:** all items with status `low`, `out` or `need`, grouped by the top-level ancestor of their location. Items without a location go under "Unassigned".
  - Every zone gets a list, even when empty. "Unassigned" appears only when it has items.
  - Each item lists the open projects (not `done` or `abandoned`) it is linked to.
  - Filtered by a shop, it keeps the items sold there plus the items with no shop set, so nothing drops off the list for want of a shop. The shopping page filters on the client; the API's `shop_id` does the same for Claude.

**Search**
- Covers project name, description and next step; item name and description; note title and body. Use SQLite FTS5.
- One FTS5 table, `search_index` (kind, record_id, title, body), kept in sync by SQLite triggers on `projects`, `items` and `notes`, so no code path can forget it. It is not a mapped model: `app/modules/search/index.py` holds its SQL, and Alembic ignores it.
  - SQLite drops a table's triggers with the table, and batch migrations rebuild tables. A migration that rebuilds `projects`, `items` or `notes` must recreate their triggers. `tests/test_db.py` fails if they're missing.
- Tokenizer `unicode61 remove_diacritics 2`: case and accents are ignored. Every word typed must match the start of a word ("tab sa" finds "Table saw"). Words are quoted, so nothing typed can use FTS5 query syntax.
- Title matches rank above body matches. Up to 5 results per kind, each with its title and the best-matching stretch of the body as plain text, matched words marked with the control characters U+0002 and U+0003. The frontend renders them as text, never HTML.
