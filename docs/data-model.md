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

Link         id, url, title,
             project_id | item_id | note_id   (exactly one set)

Attachment   id, original_filename, mime_type, size, stored_path, created_at,
             project_id | item_id | note_id   (exactly one set)
```

## Enums

| Enum | Values |
|---|---|
| `Project.status` | `someday`, `planned`, `active`, `paused`, `done`, `abandoned` |
| `Item.status` | `have`, `low`, `out`, `need` |
| `ProjectItem.requirement` | `required`, `nice_to_have` |

## Rules

**Inbox**
- Quick-add creates the real record (Project, Item or Note) with `in_inbox = true`. There is no separate capture table.
- The inbox shows every record with `in_inbox = true`. Sorting a record clears the flag.
- Inbox records still count everywhere else, including search and the shopping list.

**Items**
- Items are always created standalone. Linking to a project is a separate action (through `ProjectItem`).
- `parent_id` allows item hierarchy (e.g. table saw → blades, belts). The schema supports it in V1, while the UI only needs to show it simply.
- Prevent cycles in `parent_id`.
- Deleting an item makes its children top-level items (`parent_id` is set to null).
- New items default to status `have`. `description` is plain text and defaults to empty.
- For a `need` item, `location_id` means *where it will live*. That decides which shopping list it appears on.

**Locations**
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

**Last touched**
- `Project.last_touched_at` is set by the service layer whenever any of the following change:
  - the project itself
  - any of its notes
  - its item links
  - its links or attachments
- Each module that changes something attached to a project calls `projects.service.touch()`.
- "Stale" means an `active` or `paused` project whose `last_touched_at` is older than a threshold. The threshold is configurable and defaults to 3 weeks.

**Computed, never stored**
- **Readiness:** for a project, the count of `required` linked items with status `have` or `low`, out of all `required` linked items. Nice-to-have items are shown separately.
- **Shopping list:** all items with status `low`, `out` or `need`, grouped by the top-level ancestor of their location. Items without a location go under "Unassigned".
  - Every zone gets a list, even when empty. "Unassigned" appears only when it has items.
  - Each item lists the open projects (not `done` or `abandoned`) it is linked to.

**Search**
- Covers project name, description and next step; item name and description; note title and body. Use SQLite FTS5.
