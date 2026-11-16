# MVP (V1)

Details for each area live in `data-model.md` and `pages.md`. This file defines scope and build order.

## In scope

**Projects**
- [x] CRUD with status (someday → planned → active → paused → done/abandoned)
- [x] Next step (the first open task, v1.3.0) and last touched
- [x] List and board views, board with drag-and-drop between statuses
- [x] Tags

**Tasks** (added after V1, v1.3.0)
- [x] Tasks with a title and optional description, in a project or standalone
- [x] Ordered per project; the first open task is the project's next step
- [x] Tick off and reopen; done tasks stay on the project, collapsed
- [x] Linked items (with readiness) and tags
- [x] Tasks page, project Tasks tab, quick-add, inbox, search and MCP tools

**Items**
- [x] CRUD with status (have / low / out / need)
- [x] Parent / child hierarchy
- [x] Location (tree)
- [x] Tags
- [x] Link items to projects (required / nice-to-have)
- [x] Shops an item can be bought from (added after V1, v1.2.0)
- [x] Location tags given to items put there; parts get their parent's tags (v1.2.0)

**Locations**
- [x] Tree editor in Settings
- [x] Filtering by location includes its descendants

**Notes**
- [x] Markdown editor (headings, checkboxes, lists, etc.), stored as markdown
- [x] Optional project assignment
- [x] Notes list with project and "no project" filters

**Links and attachments**
- [x] Links on projects, items and notes
- [x] File attachments on projects, items and notes (manuals, datasheets)

**Capture and finding**
- [x] Quick-add overlay (type and name, saves to inbox)
- [x] Inbox page and icon with count
- [x] Global search (FTS5) as a command palette

**Derived views**
- [x] Project readiness
- [x] Shopping page grouped by top-level location, with "Got it"
- [x] Shopping filter by shop, across zones (v1.2.0)
- [x] Dashboard: active projects and next steps (tick off or add inline), running low, stale projects

**Platform**
- [x] HA add-on packaging, Ingress-compatible, data in `/data`
- [x] Responsive layout (desktop sidebar, mobile bottom bar)
- [x] Polish: error handling, loading states, mobile pass, first-use guidance, app icon

## Build order

Packaging and Ingress come first because they are the riskiest part. Proving the app works behind Ingress early avoids reworking routing later.

1. **Skeleton and deployment.** Scaffold the backend and frontend, have FastAPI serve the built frontend, package it as an HA add-on, and confirm it works through Ingress and the companion app.
2. **Foundations.** Database, Alembic, API client generation, app layout, navigation and theme.
3. **Locations and items.** Including the hierarchy, tags and the items list and details pages.
4. **Projects.** List, board, details and tags.
5. **Linking and derived views.** Item ↔ project links, readiness, shopping page.
6. **Notes.** Choose the editor, build the notes list and editor, and add the project Notes tab.
7. **Links and attachments.**
8. **Capture.** Quick-add, inbox and search.
9. **Dashboard.**
10. **Polish.** Mobile pass, empty states, error handling.

## Out of scope for V1

- Quantity tracking
- Custom or manual shopping lists
- Multiple users, or authentication beyond HA
- Anything in `future-enhancements.md`

## Decisions

Decided: location tags are copied to items (on create and on move, add only), including the tags of parent locations. Item tags are suggested to projects, not added. Parts get their parent item's tags (2026-11-06).

Decided: shops are their own list, many per item, managed in Settings. Filtering the shopping list by a shop spans all zones and keeps items with no shop set in their own section (2026-11-06). Prices and per-shop product links are left out.

Decided: tasks replace the free-text next step (2026-11-16). A task is a title, an optional description, linked items and tags, in a project or standalone, done or not. The next step is the project's first open task, computed, so it can't go out of date. Existing next steps became each project's first task. Done tasks are kept and shown collapsed. Due dates, subtasks and an in-progress state are left out.

Decided: stale projects default to 3 weeks, changeable in Settings (step 9).

Decided: the markdown editor is TipTap with its official markdown extension (step 6), gated by round-trip tests.
