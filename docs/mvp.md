# MVP (V1)

Details for each area live in `data-model.md` and `pages.md`. This file defines scope and build order.

## In scope

**Projects**
- [x] CRUD with status (someday → planned → active → paused → done/abandoned)
- [x] Next step (editable inline) and last touched
- [x] List and board views, board with drag-and-drop between statuses
- [x] Tags

**Items**
- [x] CRUD with status (have / low / out / need)
- [x] Parent / child hierarchy
- [x] Location (tree)
- [x] Tags
- [x] Link items to projects (required / nice-to-have)

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
- [ ] Quick-add overlay (type and name, saves to inbox)
- [ ] Inbox page and icon with count
- [ ] Global search (FTS5) as a command palette

**Derived views**
- [x] Project readiness
- [x] Shopping page grouped by top-level location, with "Got it"
- [ ] Dashboard: active projects and next steps, running low, stale projects

**Platform**
- [ ] HA add-on packaging, Ingress-compatible, data in `/data`
- [ ] Responsive layout (desktop sidebar, mobile bottom bar)

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

## Open decisions

- Default threshold for a stale project (proposed: 3 weeks; `data-model.md` already uses this as the configurable default)

Decided: the markdown editor is TipTap with its official markdown extension (step 6), gated by round-trip tests.
