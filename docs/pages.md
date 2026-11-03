# Pages and components

## Navigation

**Desktop**
- **Sidebar:** Home, Projects, Items, Notes, Shopping. Settings sits at the bottom.
- **Top bar:** search, inbox icon (with count) and a quick-add button.

**Mobile**
- **Bottom bar:** Home, Projects, **+** (quick-add, centre), Items, Shopping.
- **Top bar:** search and inbox icon. Notes and Settings are reached from a menu, or from projects and search.

**Inside the HA app**
- The app runs as an Ingress panel and must work inside the HA companion app's frame.
- It also works as a standalone browser tab or home-screen shortcut over the VPN.

## Pages

| Route | Page | Contents |
|---|---|---|
| `/` | Home | Dashboard, see below |
| `/projects` | Projects | Board (default) and list toggle; the choice is remembered per device. The board has a column per status, and dragging a card changes its status. Done and abandoned are hidden unless "Show finished" is on. Filter by tag; the list can also filter by status. Most recently touched first. Cards show status, readiness, next step and last touched |
| `/projects/:id` | Project details | Header with name, status, next step (editable) and readiness bar. Tabs: Overview (tags, description), Notes, Items (linked items with status, "link item"), Files & links. The open tab is kept in the URL. Until the markdown editor arrives (step 6) the description is a plain text box that stores markdown |
| `/items` | Items | List with location tree filter, plus status and tag filters. Child items appear indented under their parent |
| `/items/:id` | Item details | Status, location, parent and children, "Used in" (linked projects, opening their Items tab), links, attachments, description |
| `/notes` | Notes | All notes. Filter by project or "No project" |
| `/notes/:id` | Note editor | Markdown editor, project assignment, links and attachments |
| `/shopping` | Shopping | One tab per top-level location, plus "Unassigned". Opens on the first zone with something to get. Rows show where in the zone the item lives and which projects it's for. Each row has a one-tap "Got it" (sets status to `have`) with an 8-second Undo. Tapping the row opens Item details |
| `/inbox` | Inbox | Records with `in_inbox`. Inline fields to sort each one (project, location, tags) and a "Done" button that clears the flag |
| `/settings` | Settings | Location tree editor and tag management (later: export, backups) |

There is deliberately **no shopping-list item detail page**. Shopping rows are items, so they open Item details.

The **project Notes tab** reuses the Notes list component, filtered to that project, and opens the same editor.

## Dashboard (Home)

Sections in priority order:

1. **Active projects with their next step.** The next step is editable inline on the card. This is the most-used section.
2. **Running low.** A compact list (name, status badge, location) capped at about 5 to 8 items, linking to Shopping.
3. **Stale projects.** Smaller, a nudge rather than a guilt list, e.g. "Table saw restoration — 6 weeks".

No inbox section, because the inbox icon already shows the count. On mobile the sections stack in this order. On desktop, active projects take the full width with the other two side by side below.

## Overlays

- **Quick-add:** a dialog on desktop and a bottom sheet on mobile. Choose the type (Item / Note / Project), enter a name, save. Saves to the inbox and never navigates away.
- **Search:** a command palette (Ctrl+K, or the search icon). Results are grouped into projects, items and notes, and selecting one navigates to it.

## Reusable components

Generic components live in `frontend/src/components/`. Components bound to one feature's data (`ItemRow`, `LocationTreeSelect`, `TagEditor`) live in that feature's folder.

| Component | Used for |
|---|---|
| `StatusBadge` | Project and item status, colour-coded |
| `ReadinessBar` | Project cards and header. Hidden when a project has no required items |
| `TagChips` | Projects and items |
| `ProjectCard` | Projects list and board, dashboard |
| `ItemRow` | Items list, project Items tab, shopping, dashboard |
| `EntityPicker` | Search existing records with "create new" (e.g. linking items to a project) |
| `LocationTreeSelect` | Item location, items filter |
| `MarkdownEditor` | Note editor, project description |
| `LinkList` | Links on projects, items and notes |
| `AttachmentList` | Attachments on projects, items and notes |
| `PageHeader` | All pages |
| `DetailLayout` | Header plus tabs for detail pages |
| `FilterBar` | List pages |
| `EmptyState` | Any empty list |
| `ConfirmDialog` | Deletes and other destructive actions |
| `EditableText` | Names and descriptions edited in place (saves on blur or Enter) |
| `InlineAddForm` | Adding locations and tags in Settings |
| `TagEditor` | Assigning tags to projects and items, creating new ones on the fly |
| `QuickAddSheet` | Quick-add overlay |
| `SearchPalette` | Search overlay |

## Visual style

- **Base:** shadcn neutral theme (Nova preset, Geist font, lucide icons) with one accent colour: **muted blue**.
- **Light and dark:** follows the device's colour scheme. There is no manual toggle.
- **Colour:** status colours are the only other colour, so "Out", "Need" and stale projects stand out. Tokens are defined in `frontend/src/index.css` (`bg-status-green`, `text-status-red`, etc.):

  | Colour | Used for |
  |---|---|
  | Green | Item `have`, project `active` |
  | Amber | Item `low`, project `paused` |
  | Red | Item `out` |
  | Violet | Item `need`, project `planned` |
  | Orange | Stale projects |
  | Neutral (no colour) | Project `someday`, `done`, `abandoned` |

- **Layout:** generous spacing, few borders. Must be usable at phone width without horizontal scrolling.
